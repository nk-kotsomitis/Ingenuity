import copy
import enum
from tflite.Model import Model
from schema import node_schema
from configuration import *

CONVERTER_PRINT_DEBUG = False
PRINT_DES_MODEL = False
errors = 0


class TensorType(enum.Enum):
    FLOAT32 = 0
    FLOAT16 = 1
    INT32 = 2
    UINT8 = 3
    INT64 = 4
    STRING = 5
    BOOL = 6
    INT16 = 7
    COMPLEX64 = 8
    INT8 = 9
    FLOAT64 = 10
    COMPLEX128 = 11
    UINT64 = 12
    RESOURCE = 13
    VARIANT = 14
    UINT32 = 15
    UINT16 = 16
    INT4 = 17


TENSOR_TYPE_TO_NP_TYPE_MAP = {TensorType.FLOAT32: np.float32, TensorType.INT32: np.int32, TensorType.UINT8: np.uint8,
                              TensorType.INT64: np.int64, TensorType.INT16: np.int16, TensorType.INT8: np.int8}


class BuiltinOptions(enum.Enum):
    NONE = 0
    Conv2DOptions = 1
    DepthwiseConv2DOptions = 2
    ConcatEmbeddingsOptions = 3
    LSHProjectionOptions = 4
    Pool2DOptions = 5
    SVDFOptions = 6
    RNNOptions = 7
    FullyConnectedOptions = 8
    SoftmaxOptions = 9
    ConcatenationOptions = 10
    AddOptions = 11
    L2NormOptions = 12
    LocalResponseNormalizationOptions = 13
    LSTMOptions = 14
    ResizeBilinearOptions = 15
    CallOptions = 16
    ReshapeOptions = 17
    SkipGramOptions = 18
    SpaceToDepthOptions = 19


class BuiltinOperator(enum.Enum):
    ADD = 0
    AVERAGE_POOL_2D = 1
    CONCATENATION = 2
    CONV_2D = 3
    DEPTHWISE_CONV_2D = 4
    DEPTH_TO_SPACE = 5
    DEQUANTIZE = 6
    EMBEDDING_LOOKUP = 7
    FLOOR = 8
    FULLY_CONNECTED = 9
    HASHTABLE_LOOKUP = 10
    L2_NORMALIZATION = 11
    L2_POOL_2D = 12
    LOCAL_RESPONSE_NORMALIZATION = 13
    LOGISTIC = 14
    LSH_PROJECTION = 15
    LSTM = 16
    MAX_POOL_2D = 17
    MUL = 18
    RELU = 19
    RELU1 = 20
    RELU6 = 21
    RESHAPE = 22
    RESIZE_BILINEAR = 23
    RNN = 24
    SOFTMAX = 25
    SPACE_TO_DEPTH = 26
    SVDF = 27
    TANH = 28
    CONCAT_EMBEDDINGS = 29
    SKIP_GRAM = 30
    CALL = 31
    CUSTOM = 32


def _convert_np_array_datatype(nd_array_bytes, nd_data_type):
    return nd_array_bytes.view(nd_data_type)


def _deserialize_tensor_name(name_str):
    act_function = []

    # Keywords to search for
    # keywords = ['MatMul', 'BiasAdd', 'Relu']
    # TODO
    keywords = ['Relu']
    # Split the string by ';'
    segments = name_str.split(';')
    # Dictionary to store found keywords
    found_keywords = {keyword: [] for keyword in keywords}

    # Process each segment
    for segment in segments:
        # Split the segment by '/' into parts
        parts = segment.split('/')
        for part in parts:
            # Check if the part is one of the keywords
            if part in keywords:
                found_keywords[part].append(segment)

    # Print the results
    for keyword, segment in found_keywords.items():
        # print(f"{keyword}: {segment}")
        if segment:
            act_function.append(keyword)

    if len(act_function) > 1:
        print("Error: More than 1 activation function found during tensor's name deserialization!")
    elif len(act_function) == 0:
        return np.array((0,), dtype=np.int8)
    else:
        # TODO: Enum for activation functions, For now RELU = 1
        # return act_function[0]
        return np.array((1,), dtype=np.int8)


def _deserialize_tf_lite_model(tflite_model):
    global errors

    # Main variables
    model_layers = []

    # Secondary variables
    model_tensors = []
    model_ops = []
    model_ops_codes = []
    model_inputs = []
    model_outputs = []
    root_buffer = []

    if CONVERTER_PRINT_DEBUG:
        print('************************************* Part 1: De-serialize model **************************************\n\n')

    # ********************** Load model *************************
    # Load the .tflite model file
    with open(tflite_model, 'rb') as f:
        model_data = f.read()
    # Get the root of the FlatBuffer
    model = Model.GetRootAsModel(model_data, 0)

    # ****************** Description Version ********************
    if CONVERTER_PRINT_DEBUG:
        print(f"Version: {model.Version()}")
        print(f"Description: {model.Description().decode('utf-8')}")

    # ****************** Operator Codes (1) *********************
        print(f"OperatorCodes ({model.OperatorCodesLength()})")
    # A list of all operator codes used in this model.
    # This is kept in order because operators carry an index into this vector.
    for i in range(model.OperatorCodesLength()):
        op_code = model.OperatorCodes(i)
        if CONVERTER_PRINT_DEBUG:
            print("\t", i,
                  "- OperatorCode: BuiltinOperator = ", BuiltinOperator(op_code.BuiltinCode()),
                  "- CustomCode  = ", op_code.CustomCode())
        model_ops_codes.append(op_code)

    # ****************** Metadata *******************************
    if CONVERTER_PRINT_DEBUG:
        print(f"Metadata ({model.MetadataLength()})")
    for i in range(model.MetadataLength()):
        meta = model.Metadata(i)
        if CONVERTER_PRINT_DEBUG:
            print("\t", i, "Metadata:", meta.Name())

    # ****************** Signature  Def *************************
    if CONVERTER_PRINT_DEBUG:
        print(f"Signature Def ({model.SignatureDefsLength()})")
    for i in range(model.SignatureDefsLength()):
        signature_def = model.SignatureDefs(i)
        if CONVERTER_PRINT_DEBUG:
            print("\t", i, "Signature Def:", signature_def.SignatureKey())

    # ********************** Subgraphs (1) **********************
    if CONVERTER_PRINT_DEBUG:
        print(f"Subgraphs ({model.SubgraphsLength()})")
    for i in range(model.SubgraphsLength()):
        subgraph = model.Subgraphs(i)
        if CONVERTER_PRINT_DEBUG:
            print("\t", i, "- Subgraph:", subgraph.Name().decode('utf-8'))

        # ************ Tensors (33) ************
        if CONVERTER_PRINT_DEBUG:
            print(f"\t\tTensors ({subgraph.TensorsLength()})")
        for j in range(subgraph.TensorsLength()):
            tensor = subgraph.Tensors(j)
            # print("\t\t\tName:", tensor.Name())
            # print("\t\t\tBufferIndex:", tensor.Buffer())
            # print("\t\t\tShape:", tensor.ShapeAsNumpy())  # NHWC (?)
            # print("\t\t\tType:", TensorType(tensor.Type()))
            if CONVERTER_PRINT_DEBUG:
                print("\t\t\tTensor:", j, tensor.Buffer(), tensor.Name(), tensor.ShapeAsNumpy(), TensorType(tensor.Type()))

            q_params = tensor.Quantization()
            if q_params is not None and False:
                print("\t\t\tQParams:",
                      tensor.Quantization().ScaleAsNumpy(),
                      tensor.Quantization().ZeroPointAsNumpy(),
                      tensor.Quantization().MinAsNumpy(),
                      tensor.Quantization().MaxAsNumpy())
            # print()

            q_params_dict = {}
            if q_params is not None:
                q_params_dict = {'scale': tensor.Quantization().ScaleAsNumpy(),
                                 'zero_point': tensor.Quantization().ZeroPointAsNumpy(),
                                 'min': tensor.Quantization().MinAsNumpy(),
                                 'max': tensor.Quantization().MaxAsNumpy()}

            # Store tensor indices
            tensor = {'name': tensor.Name(),
                      'index': j,  # This is the incremental index
                      'buffer_index': tensor.Buffer(),  # This is the root buffer index
                      'shape': tensor.ShapeAsNumpy(),
                      'type': TensorType(tensor.Type()),
                      'q_params': q_params_dict,
                      'buffer': None}
            model_tensors.append(tensor)

        # ************ Inputs/Outputs ************
        if CONVERTER_PRINT_DEBUG:
            print("\t\tInputs:", subgraph.InputsLength())
        for j in range(subgraph.InputsLength()):
            if CONVERTER_PRINT_DEBUG:
                print("\t\t\t", j, "Input:", subgraph.Inputs(j))
            model_inputs.append(subgraph.Inputs(j))

        if CONVERTER_PRINT_DEBUG:
            print("\t\tOutputs:", subgraph.OutputsLength())
        for j in range(subgraph.OutputsLength()):
            if CONVERTER_PRINT_DEBUG:
                print("\t\t\t", j, "Output:", subgraph.Outputs(j))
            model_outputs.append(subgraph.Outputs(j))

        # *************** Operators ***************
        if CONVERTER_PRINT_DEBUG:
            print("\t\tOperators:", subgraph.OperatorsLength())
        for j in range(subgraph.OperatorsLength()):
            operator = subgraph.Operators(j)
            if CONVERTER_PRINT_DEBUG:
                print("\t\t\tOpCodeIndex:", operator.OpcodeIndex())
                print("\t\t\tInputs:", operator.InputsAsNumpy())
                print("\t\t\tOutputs:", operator.OutputsAsNumpy())
                print("\t\t\tBuiltinOptionsType:", BuiltinOptions(operator.BuiltinOptionsType()))
                print("\t\t\tCustomOptions", operator.CustomOptionsAsNumpy())
                print("\t\t\tMutatingVariableInputsLength", operator.MutatingVariableInputsLength())
                print("\t\t\tIntermediatesLength", operator.IntermediatesLength())
                print()

            op = {'index': operator.OpcodeIndex(),
                  'inputs': operator.InputsAsNumpy(),
                  'outputs': operator.OutputsAsNumpy(),
                  'type': operator.BuiltinOptionsType()}
            model_ops.append(op)

    if CONVERTER_PRINT_DEBUG:
        print('************************************* Part 2: De-serialize buffers ************************************\n\n')

    # ********************** Root Buffer **********************
    if CONVERTER_PRINT_DEBUG:
        print(f"Buffers ({model.BuffersLength()})")

    # 1. Save all buffers in a list
    for i in range(model.BuffersLength()):
        buffer = model.Buffers(i)
        root_buffer.append(buffer.DataAsNumpy())
        # print("DEBUG", i, )

    # 2. Map the tensor's buffer index with the root buffer
    for i, tensor in enumerate(model_tensors):
        buf_idx = tensor['buffer_index']
        tensor['buffer'] = copy.deepcopy(root_buffer[buf_idx])  # index is for the root buffer
        # tensor['index'] -= 1  # This is because the first buffer is empty by default
        # print(f"DEBUG {i} - {tensor['index']} - {tensor['buffer_index']} - {tensor['shape']} - {tensor['name']} - {tensor['type']}:")

    # 3. Re-order the buffers based on operators
    for op in model_ops:
        layer = {}

        inputs = op['inputs']
        outputs = op['outputs']
        type = op['type']
        op_code = model_ops_codes[op['index']]

        if CONVERTER_PRINT_DEBUG:
            print("Operator", inputs, outputs, "\t\t\t", BuiltinOperator(op_code.BuiltinCode()))

        # TODO: Implement 'type' and 'op_code'

        # Inputs: I, W, B
        for i, input in enumerate(inputs):
            if i == 0:
                layer['I'] = copy.deepcopy(model_tensors[input])
            elif i == 1:
                layer['W'] = copy.deepcopy(model_tensors[input])
            elif i == 2:
                layer['B'] = copy.deepcopy(model_tensors[input])
            else:
                print("Error: More than 3 input tensor exists! Why?")
                errors += 1

        # Outputs: O
        for i, output in enumerate(outputs):
            if i == 0:
                layer['O'] = copy.deepcopy(model_tensors[output])
            else:
                print("Error: More than 1 output tensor exists! Why?")
                errors += 1

        model_layers.append(layer)

    if PRINT_DES_MODEL:
        # Print de-serialized model
        for layer in model_layers:
            for keys, values in layer.items():
                print(keys, values)
            print()
        print()

    return model_layers


def _convert_to_my_model_schema(model):
    """
    # IMPORTANT NOTE: All the data types at MyFormat, are as taken from the model and converted in np format
    # IMPORTANT NOTE: Buffers are converted to their respective data type

    :param model:
    :return:
    """
    global errors

    # Main variables
    new_model = []

    if CONVERTER_PRINT_DEBUG:
        print('*************************************** Part 3: Convert model *****************************************\n\n')

    # ************************** Layers ****************************
    for i, layer in enumerate(model):
        # Node schema
        node = copy.deepcopy(node_schema)

        # Attributes
        node['attributes']['conversion'] = False

        # Convert Layer to myFormat
        for layer_key, layer_value in layer.items():
            # ************************************ I ***************************************
            if layer_key == 'I':
                node['inputs']['a1']['type'] = TENSOR_TYPE_TO_NP_TYPE_MAP[layer_value['type']]  # np data type
                node['inputs']['a1']['shape'] = layer_value['shape']
                if layer_value['q_params']:
                    node['inputs']['a1']['q_params']['scale'] = layer_value['q_params']['scale']
                    node['inputs']['a1']['q_params']['zero'] = layer_value['q_params']['zero_point']
                    node['inputs']['a1']['q_params']['min'] = layer_value['q_params']['min']
                    node['inputs']['a1']['q_params']['max'] = layer_value['q_params']['max']
            # ************************************ W ***************************************
            elif layer_key == 'W':
                node['inputs']['weights']['type'] = TENSOR_TYPE_TO_NP_TYPE_MAP[layer_value['type']]  # np data type
                node['inputs']['weights']['shape'] = layer_value['shape']
                # node['inputs']['weights']['buffer'] = layer_value['buffer'].astype(TENSOR_TYPE_TO_NP_TYPE_MAP[layer_value['type']])
                node['inputs']['weights']['buffer'] = _convert_np_array_datatype(layer_value['buffer'],
                                                                                TENSOR_TYPE_TO_NP_TYPE_MAP[layer_value['type']])

                # print("MY_TEST:", type(node['inputs']['weights']['buffer'].dtype), node['inputs']['weights']['buffer'])
                if layer_value['q_params']:
                    node['inputs']['weights']['q_params']['scale'] = layer_value['q_params']['scale']
                    node['inputs']['weights']['q_params']['zero'] = layer_value['q_params']['zero_point']
                    node['inputs']['weights']['q_params']['min'] = layer_value['q_params']['min']
                    node['inputs']['weights']['q_params']['max'] = layer_value['q_params']['max']
            # ************************************ B ***************************************
            elif layer_key == 'B':
                node['inputs']['bias']['type'] = TENSOR_TYPE_TO_NP_TYPE_MAP[layer_value['type']]  # np data type
                node['inputs']['bias']['shape'] = layer_value['shape']
                node['inputs']['bias']['buffer'] = layer_value['buffer']
                node['inputs']['bias']['buffer'] = _convert_np_array_datatype(node['inputs']['bias']['buffer'],
                                                                             TENSOR_TYPE_TO_NP_TYPE_MAP[layer_value['type']])

                # print("MY_TEST:", type(node['inputs']['bias']['buffer'].dtype), node['inputs']['bias']['buffer'])
                if layer_value['q_params']:
                    node['inputs']['bias']['q_params']['scale'] = layer_value['q_params']['scale']
                    node['inputs']['bias']['q_params']['zero'] = layer_value['q_params']['zero_point']
                    node['inputs']['bias']['q_params']['min'] = layer_value['q_params']['min']
                    node['inputs']['bias']['q_params']['max'] = layer_value['q_params']['max']
            # ************************************ O ***************************************
            elif layer_key == 'O':
                node['outputs']['a2']['type'] = TENSOR_TYPE_TO_NP_TYPE_MAP[layer_value['type']]  # np data type
                node['outputs']['a2']['shape'] = layer_value['shape']
                node['outputs']['a2']['actf'] = _deserialize_tensor_name(str(layer_value['name']))
                if layer_value['q_params']:
                    node['outputs']['a2']['q_params']['scale'] = layer_value['q_params']['scale']
                    node['outputs']['a2']['q_params']['zero'] = layer_value['q_params']['zero_point']
                    node['outputs']['a2']['q_params']['min'] = layer_value['q_params']['min']
                    node['outputs']['a2']['q_params']['max'] = layer_value['q_params']['max']
            else:
                print("Error TODO")
                errors += 1
        # print(node)
        new_model.append(node)

    return new_model


def model_converter(tflite_model):

    tflite_des = _deserialize_tf_lite_model(tflite_model)

    model_converted = _convert_to_my_model_schema(tflite_des)

    return model_converted
