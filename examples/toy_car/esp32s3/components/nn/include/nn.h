/*
 * nn.h
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
 
#ifndef NN_H
#define NN_H

#include <stdint.h>

#define NUM_OF_LAYERS 10
#define CONVERSION 0
#define CARRAY_W_LENGTH 264194
#define CARRAY_B_LENGTH 1674
#define CARRAY_A_LENGTH 1282
#define CARRAY_SM_LENGTH 42
#define CARRAY_ZF_LENGTH 2632
#define CARRAY_A_A1 0
#define CARRAY_A_A2 640
#define CARRAY_ALIGN 16
#define INPUT_LENGTH 640
#define OUTPUT_LENGTH 640
#define INPUT_SCALE 0.3910152316093445
#define INPUT_ZERO_POINT 89
#define OUTPUT_SCALE 0.36449846625328064
#define OUTPUT_ZERO_POINT 96


typedef int8_t Weights_t;
typedef int32_t Bias_t;
typedef int8_t In_out_t;
typedef uint16_t Shapes_m_t;
typedef int32_t Zero_actf_t;
typedef float Scales_t;



typedef enum
{
    NN_LITE_ERROR = 0,
    NN_LITE_SUCCESS = 1
} NN_lite_res_t_;
typedef int32_t NN_lite_res_t; // DEBUG

extern In_out_t c_array_a[] __attribute__((aligned(CARRAY_ALIGN))); 
extern Weights_t c_array_w[] __attribute__((aligned(CARRAY_ALIGN))); 
extern Shapes_m_t c_array_sm[] __attribute__((aligned(CARRAY_ALIGN))); 
extern Bias_t c_array_b[] __attribute__((aligned(CARRAY_ALIGN))); 
extern Zero_actf_t c_array_zf[] __attribute__((aligned(CARRAY_ALIGN))); 

// Assembly
int8_t nn_asm(Shapes_m_t const *p_shapes, 
                Zero_actf_t const *p_zf, 
                In_out_t *p_a1, 
                Weights_t const *p_weights, 
                Bias_t const *p_biases, 
                In_out_t *p_a2); 

#endif // NN_H
