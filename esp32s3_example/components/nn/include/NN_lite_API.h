 /*
 * NN_lite_API.h
 *
 *  Created on: Jan 1, 2025
 *      Author: NN
 */

#ifndef NN_LITE_API_H
#define NN_LITE_API_H

typedef enum
{
    NN_LITE_ERROR = 0,
    NN_LITE_SUCCESS = 1
} NN_lite_res_t;

typedef int8_t In_out_t;

#define NN_LITE_INPUT_LENGTH 640
#define NN_LITE_OUTPUT_LENGTH 640

NN_lite_res_t NN_lite_inference(In_out_t *input, In_out_t **output);

#endif /* NN_LITE_API_H */
