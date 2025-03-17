/*
 * NN_lite_API.h
 *
 * Copyright (C) 2025 Ingenuity
 *
 * This file is part of Ingenuity.
 *
 * Ingenuity is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ingenuity is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Ingenuity.  If not, see <https://www.gnu.org/licenses/>.
 */

#ifndef NN_LITE_API_H
#define NN_LITE_API_H

/** 
 * @brief Result type for the inference
 */
typedef enum
{
    NN_LITE_ERROR = 0,
    NN_LITE_SUCCESS = 1
} NN_lite_res_t;

/** Type used for input/output buffer data (int8) */
typedef int8_t In_out_t;

/** The input buffer length */
#define NN_LITE_INPUT_LENGTH 640
/** The output buffer length */
#define NN_LITE_OUTPUT_LENGTH 640

/**
 * @brief Retrieves the pointer to the input buffer with a length of NN_LITE_INPUT_LENGTH
 *
 * @return A pointer to the input buffer.
 */
In_out_t *NN_lite_get_p_input();

/**
 * @brief Quantize a floating-point value to int8.
 *
 * This function uses the model's input scale and zero-point for the quantization process.
 *
 * @param input The floating-point value to be quantized.
 *
 * @return The quantized int8 value.
 */
In_out_t NN_lite_quantize_FloatToInt(float input);

/**
 * @brief Performs inference on the model
 *
 * This function runs the model on the input data and generates the output.
 *
 * @return The result of the inference, represented by a status code from the NN_lite_res_t type.
 *         NN_LITE_SUCCESS indicates successful inference, while NN_LITE_ERROR indicates a failure.
 */
NN_lite_res_t NN_lite_inference();

/**
 * @brief De-quantize an int8 value to a floating-point value.
 *
 * This function uses the model's output scale and zero-point for the de-quantization process.
 *
 * @param output The int8 value to be de-quantized.
 *
 * @return The de-quantized floating-point value.
 */
float NN_lite_dequantize_IntToFloat(In_out_t output);

/**
 * @brief Retrieves the pointer to the output buffer with a length of NN_LITE_OUTPUT_LENGTH
 *
 * @return A pointer to the output buffer.
 */
In_out_t *NN_lite_get_p_output();

#endif /* NN_LITE_API_H */
