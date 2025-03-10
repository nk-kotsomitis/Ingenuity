
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

#include "include/nn.h"

NN_lite_res_t NN_lite_inference(In_out_t *input, In_out_t **output)
{		
    // Result
    NN_lite_res_t res = NN_LITE_ERROR;

    // Buffer Pointers
    Weights_t const *p_weights = &c_array_w[0];
    Bias_t const *p_biases = &c_array_b[0];
    Shapes_m_t const *p_shapes = &c_array_sm[0];
    Zero_actf_t const *p_zf = &c_array_zf[0];
    In_out_t *p_a1 = &c_array_a[CARRAY_A_A1];
    In_out_t *p_a2 = &c_array_a[CARRAY_A_A2];

    // Input
    for (uint16_t i = 0; i < INPUT_LENGTH; i++)
    {
        *(p_a1++) = input[i];
    }

    p_a1 = &c_array_a[CARRAY_A_A1];

    // Invoke	
    res = nn_asm(p_shapes, p_zf, p_a1, p_weights, p_biases, p_a2);

    // printf("\n\nRes = 0x%"PRIx32"  %"PRId32"\n", res, res); // Debug

    // Output
    if (c_array_sm[0] % 2)
    {
        *output = &c_array_a[CARRAY_A_A2];	
    }
    else
    {
        *output = &c_array_a[CARRAY_A_A1];
    }

    return res;		
}
    