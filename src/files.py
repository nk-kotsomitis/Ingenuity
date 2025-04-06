# Copyright (C) 2025 Ingenuity
# Licensed under the GNU General Public License v3.0

EXAMPLE_MAIN_C = """
/*
 * main.c
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
 
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include "freertos/projdefs.h"

#include "../components/nn/include/NN_lite_API.h"

void app_main(void)
{
    NN_lite_res_t res = NN_LITE_ERROR;
    In_out_t *input = NULL;
    In_out_t *output = NULL;

    while(1)
    {
        // Get the pointer for the input
        input = NN_lite_get_p_input();
        
        // Set the input
        for (uint16_t i = 0; i < NN_LITE_INPUT_LENGTH; i++) 
        {
            input[i] = i;
        }
        
        // Invoke inference
        res = NN_lite_inference();
        
        if (res != NN_LITE_SUCCESS)
        {
            printf("Inference failed: %d", res);
            return;
        }
        else
        {
            printf("Inference succeeded!\\r\\n");
        }
                
        // Get the pointer for the input
        output = NN_lite_get_p_output();
        
        // Get the output
        for (uint16_t i = 0; i < NN_LITE_OUTPUT_LENGTH; i++) 
        {
            // printf("%d ", output[i]);
        }
        printf("\\r\\n");
        
        vTaskDelay(pdMS_TO_TICKS(3000));
    }
}
"""

VALIDATION_MAIN_C = """
/*
 * main.c
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
 
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "freertos/projdefs.h"
#include "validation.h"
#include "../components/nn/include/NN_lite_API.h"

void app_main(void)
{
    NN_lite_res_t res = NN_LITE_ERROR;
    In_out_t *input = NULL;
    In_out_t *output = NULL;
    
    vTaskDelay(pdMS_TO_TICKS(500));
    
    uint32_t inferences_n = {inferences_n};
    
    while(inferences_n)
    {
        for(uint32_t dataset_idx = 0; dataset_idx < DATASET_LEN; dataset_idx++)
        {
            // Get the pointer for the input
            input = NN_lite_get_p_input();

            // Set validation input
            val_set_input(&input, dataset_idx);
    
            // Start cycles counter
            val_inference_start();
    
            // Inference
            res = NN_lite_inference();
    
            // Stop cycles counter
            val_inference_end(dataset_idx);
            
            // Get the pointer for the input
			output = NN_lite_get_p_output();
			
            // Set validation output
            val_output(output, dataset_idx);
    
            vTaskDelay(pdMS_TO_TICKS({inference_rate}));
            
            inferences_n--;
            if(!inferences_n)
            {
                break;
            }
        }
    }
}
"""


NN_MODEL_C = """
/*
 * nn.c
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
 
#include <stdint.h>
#include "include/nn.h"

{c_arrays}

"""

NN_C = """
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
 
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <math.h>

#include "include/nn.h"

In_out_t *NN_lite_get_p_input()
{
	return &c_array_a[CARRAY_A_A1];
}

In_out_t NN_lite_quantize_FloatToInt(float input)
{
	return (In_out_t)(round((input / INPUT_SCALE) + INPUT_ZERO_POINT));
}

NN_lite_res_t NN_lite_inference()
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
	
    // Invoke	
    res = nn_asm(p_shapes, p_zf, p_a1, p_weights, p_biases, p_a2);
    // printf("\\n\\nRes = 0x%"PRIx32"  %"PRId32"\\n", res, res); // Debug
	
    return res;		
}

float NN_lite_dequantize_IntToFloat(In_out_t output)
{
	return ((float)output - (float)OUTPUT_ZERO_POINT) * OUTPUT_SCALE;
}

In_out_t *NN_lite_get_p_output()
{
    if (c_array_sm[0] % 2)
    {
        return &c_array_a[CARRAY_A_A2];	
    }
    else
    {
        return &c_array_a[CARRAY_A_A1];
    }	
}
    """


NN_H = """\
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

{definitions}

{typedefs}


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
"""


NN_API_H = """\
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
#define NN_LITE_INPUT_LENGTH {input_length}
/** The output buffer length */
#define NN_LITE_OUTPUT_LENGTH {output_length}

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
"""


NN_ASM = """
# nn_asm.s
#
# Copyright (C) 2025 Ingenuity
#
# This file is part of Ingenuity.
#
# Ingenuity is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ingenuity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ingenuity.  If not, see <https://www.gnu.org/licenses/>.

	.section	".text"
	.align	4
	.global	nn_asm
	.type	nn_asm, @function
nn_asm:
	entry	sp, 96
	mov	   	a1, sp
	
	/*
	a2  - pointer_sm
	a3  - pointer_zf
	a4  - pointer_a1
	a5  - pointer_w
	a6  - pointer_b
	a7  - pointer_a2
   *a8  - temp
   *a9  - temp
	a10 - mul_64
	a11 - mul_8
   *a12 - temp/acc_res
   *a13 - free!!!
	a14 - y_params (32-bit)
   *a15 - acc/loop_counter

	f0 - pointer_a1
	f1 - pointer_a2
	f2 - layers
	f3 - helper 1
	f5 - col_w_rem
	f6 - col_w
	f7 - ymax
	f8 - pointer_a1_temp
	f9 - acc init
	f10 - act_function
	f11 - zero_point_2
	f12 - y_mul_0
	f13 - y_mul_1
	f14 - y_mul_2
	f15 - y_mul_3
	rc < 64 => (0 		  [1-8])
	rc = 64 => (0 		     8 )
	rc > 64 => ([1-65535] [1-8])
	*/
		
STATE_INIT:
	wfr f0, a4			// f0 = pointer_a1
	wfr f1, a7			// f1 = pointer_a2

	l16ui a9,  a2, 0	// a9 = pointer_sm[0] = layers_n
	addi  a2,  a2, 2	// pointer_sm += 2
	wfr   f2, a9		// f2 = layers

	movi a9, 1
	wfr f3, a9			// f3 = 1 (helper variable)

	movi a9, 3
	wsr.br a9			// br = 0000 0000 0000 0011

# ------------------------------------------
# ------------- 0.Initialization -----------
# ------------------------------------------
ST_LAYER_START:

	# ------------ Swap Pointers -----------
	xorb b0, b0, b1			// b0 ^= b1 (toggle bit)
	bf b0, POINTERS			// if b0 == 0, jump

	rfr a7, f0 				// a7 = f0 = p_a1
	rfr a4, f1 				// a4 = f1 = p_a2
	j POINTERS_END
POINTERS:
	rfr a4, f0 				// a4 = f0 = p_a1
	rfr a7, f1 				// a7 = f1 = p_a2
POINTERS_END:

	# ------------ Layers -------------------
	sub.s f2, f2, f3		// Decrement layer

	# ------------ SM array (a2) ------------
	l16ui  a12,  a2, 0		// a12 = col_w_rem
	wfr    f5,   a12		// f5  = col_w_rem
	l16ui  a12, a2, 2		// a12 = col_w
	wfr    f6,   a12		// f6  = col_w
	l16ui  a10, a2, 4		// a10 = mul_64
	l16ui  a11, a2, 6		// a11 = mul_8
	addi   a2,  a2, 8		// pointer_sm += 8

	# ------------ ZF array (a3) ------------
	l32i  a13, a3, 0		// a13  = activation
	wfr f10, a13

	l32i  a13, a3, 4		// a13  = zero_point_2
	wfr f11, a13

	l32i  a14, a3, 8		// a14  = y_params

	l32i  a9,  a3, 12		// a14  = y_mul_0
	wfr f12, a9
	
	l32i  a9,  a3, 16		// a14  = y_mul_1
	wfr f13, a9
	
	l32i  a9,  a3, 20		// a14  = y_mul_2
	wfr f14, a9
	
	l32i  a9,  a3, 24		// a14  = y_mul_3
	wfr f15, a9
	
	addi   a3, a3, 28		// pointer_zf += 7
	#addi   a3, a3, 1024		// pointer_zf += 256
# ------------------------------------------
# ------------- 1.Multiplication -----------
# ------------------------------------------

ST_MATRIX_START:
	ee.zero.accx						// accx = 0
	wfr f8, a4
	sub.s f6, f6, f3					// layers_n--
	movi a15, 0 						// a15 = loop counter = 0

	beq a10, a15, ST_QR_BLOCK_8B_INIT	// if mul_64 == counter == 0, jump

ST_QR_BLOCK_64B:

	addi a15, a15, 1

	ee.vld.128.ip q0, a4, 16
	ee.vld.128.ip q1, a5, 16
	ee.vld.128.ip q2, a4, 16
	ee.vld.128.ip q3, a5, 16
	ee.vld.128.ip q4, a4, 16
	ee.vld.128.ip q5, a5, 16
	ee.vld.128.ip q6, a4, 16
	ee.vld.128.ip q7, a5, 16

	ee.vmulas.s8.accx q0, q1
	ee.vmulas.s8.accx q2, q3
	ee.vmulas.s8.accx q4, q5
	ee.vmulas.s8.accx q6, q7

	bne a15, a10, ST_QR_BLOCK_64B		// if counter == mul_64, jump

ST_QR_BLOCK_8B_INIT:
	movi a15, 0
	ee.zero.q q0
	ee.zero.q q1

ST_QR_BLOCK_8B:

	ee.vld.l.64.ip q0, a4, 8
	ee.vld.l.64.ip q1, a5, 8
	addi a15, a15, 1
	ee.vmulas.s8.accx q0, q1

	bne a15, a11, ST_QR_BLOCK_8B		// if counter == mul_8, jump

ST_QR_BLOCK_END:

	rur.accx_0 a15		// Read ACCX_0
	#rur.accx_1 a15		// Read ACCX_1
	l32i a9, a6, 0		// a9 = ZeroBias
	addi a6, a6, 4		// ZeroBias_pointer++
	add a15, a15, a9 	// acc = acc + ZeroBias

# ------------------------------------------
# ------------- 2.Activation  --------------
# ------------------------------------------
	// ONLY FOR SINE WAVE
	#rfr a9, f2					// a9 = f2 = layers_n
	#beqz a9, ACT_FUNC_NONE		// if a9 == 0, jump (i.e. last layer)

	#extui  a9, a13, 16, 8			// a9 = act_function
	rfr a9, f10
	bnei a9, 1, ACT_FUNC_NONE		// if act_funtion != 1, jump

ACT_FUNC_RELU:
	movi a9, 0				// a9 = 0
	movltz	a15, a9, a15	// acc = (acc >= 0) ? acc : 0;
ACT_FUNC_NONE:


# ------------------------------------------
# ------------- 2.De-quantization ----------
# ------------------------------------------
	wfr    f9, a15 // accum init

	beqz a15, DEQUANTIZATION_ZERO_POINT

DEQUANTIZATION:

	# 1 reg: a15 acc
	# 2 reg: a9 y
	# 3 reg: a12 res
 	# 4 reg: a8 y_mul_x

	bltz a15, DEQUANTIZATION_NEGATIVE_ACC

	# ********** Positive ACC ********************

	# ******* res = acc * y_mul_0 *******
	movi   a12, 0		// res
	rfr a8, f12
	mull a12, a15, a8	// mull


	# ******* res = acc * y_mul_1 *******
	extui  a9, a14, 0, 8	// a9 = y1
	wsr.sar	   a9				// SAR = y1
	sra    a15, a15			// a9 = acc >> y1

	rfr a8, f13
	mull  a9, a15, a8		// mull
	add a12, a12, a9		// a12 += a8


	# ******* res = acc * y_mul_2 *******
	extui  a9, a14, 8, 8	// a9 = y1
	wsr.sar 	   a9				// SAR = y1
	sra    a15, a15			// a9 = acc >> y1

	rfr a8, f14
	mull  a9, a15, a8		// mull
	add a12, a12, a9		// a12 += a8


	# ******* res = acc * y_mul_3 *******
	extui  a9, a14, 16, 8	// a9 = y1
	wsr.sar 	   a9				// SAR = y1
	sra    a15, a15			// a9 = acc >> y1

	rfr a8, f15
	mull  a9, a15, a8		// mull
	add a12, a12, a9		// a12 += a8

j DEQUANTIZATION_Y_MAX
	# ********** Negative ACC ********************
DEQUANTIZATION_NEGATIVE_ACC:
		
	# ******* res = acc * y_mul_0 *******
	movi   a12, 0		// res
	rfr a8, f12
	mull a12, a15, a8	// mull

	# ******* res = acc * y_mul_1 *******
	extui  a9, a14, 0, 8	// a9 = y1
	wsr.sar 	   a9				// SAR = y1
	neg    a15, a15
	sra    a15, a15			// a9 = acc >> y1
	addi a15, a15, 1
	neg    a15, a15
	
	rfr a8, f13
	mull  a9, a15, a8		// mull
	add a12, a12, a9		// a12 += a8


	# ******* res = acc * y_mul_2 *******
	extui  a9, a14, 8, 8	// a9 = y1
	wsr.sar 	   a9				// SAR = y1
	neg    a15, a15
	sra    a15, a15			// a9 = acc >> y1
	addi a15, a15, 1
	neg    a15, a15

	rfr a8, f14
	mull  a9, a15, a8		// mull
	add a12, a12, a9		// a12 += a8


	# ******* res = acc * y_mul_3 *******
	extui  a9, a14, 16, 8	// a9 = y1
	wsr.sar 	   a9				// SAR = y1
	neg    a15, a15
	sra    a15, a15			// a9 = acc >> y1
	addi a15, a15, 1
	neg    a15, a15

	rfr a8, f15
	mull  a9, a15, a8		// mull
	add a12, a12, a9		// a12 += a8

DEQUANTIZATION_Y_MAX:

	bltz a12, DEQUANTIZATION_Y_MAX_POSITIVE
	
	# ******* Positive res Y_max *********************
	extui  a9, a14, 24, 8	// a9 = y_max
	#ssr	a9					// SAR = y_max
	wsr.sar a9
	sra  a15, a12			// res >> ymax

	j DEQUANTIZATION_ZERO_POINT
DEQUANTIZATION_Y_MAX_POSITIVE:

	# ******* Negative res Y_max *********************
	extui  a9, a14, 24, 8	// a9 = y_max
	#ssr	a9					// SAR = y_max
	wsr.sar a9
	neg a12, a12
	sra  a12, a12			// res >> ymax
	addi a15, a15, 1
	neg  a15, a12

DEQUANTIZATION_ZERO_POINT:
	rfr a9, f11
	add  a15, a15, a9		// a15 = acc + zero_point_a2

	rfr a12, f9 // accum
	beqz a12, LUT_END
	
	# TODO: This checks if it's the last layer. 
	# To be changed to jump if the accumulator is negative TBC
	rfr a9, f2
	beqz a9, LUT_LAST
	
	
LUT:
	addi a13, a15, 128		// idx = res + 128 [0 - 255]
	slli a13, a13, 2        // idx * 4 bytes
	add a3, a3, a13			// a3 = a3 + idx
	l32i a9, a3, 0
	neg a13, a13
	add a3, a3, a13

	rfr a12, f9					// a12 = accum
	blt a12, a9, LUT_END		// a12 = accum, a9 = limit,   if (accum >= limit)  res++
    addi a15, a15, 1 // res++
		
LUT_END:
	j CLIPPING

LUT_LAST:	
	addi a13, a15, 127		// idx = res + 128 [0 - 255]
    slli a13, a13, 2        // idx * 4 bytes
	add a3, a3, a13			// a3 = a3 + idx
	l32i a9, a3, 0
	neg a13, a13
	add a3, a3, a13

	rfr a12, f9					// a12 = accum
	bge a12, a9, CLIPPING
    addi a15, a15, -1 // res++

CLIPPING:
    movi a9, 127
    blt a15, a9, CHECK_LOWER_BOUND
    movi a15, 127
    j DEQUANTIZATION_END
CHECK_LOWER_BOUND:
    movi a9, -128
    bge a15, a9, DEQUANTIZATION_END
    movi a15, -128

DEQUANTIZATION_END:

# --------------------------------------------
# ------------------------------------------
# ------------- 3.Write --------------------
# ------------------------------------------

	s8i a15, a7, 0					// Write to A2
	addi a7, a7, 1					// Forward A2

	rfr a4, f8
	#mov a4, a8						// a4 = a8 = pointer_a1
	rfr a9, f6
	bgei a9, 1, ST_MATRIX_START		// If col_w >= 0, jump

ST_MATRIX_MUL_END:

	rfr a9, f5						// a9 = f5 = col_w_rem
	movi a15, 0

ST_MATRIX_REM_START:
	beqz a9, ST_MATRIX_REM_END

	s8i a15, a7, 0
	addi a7, a7, 1
	addi a9, a9, -1

	j ST_MATRIX_REM_START

ST_MATRIX_REM_END:

	addi  a3, a3, 1024				// pointer_zf += 256 * 4 1024
	# addi  a1, a1, 16				

	rfr a9, f2						// a9 = f2 = layers
	bnez a9, ST_LAYER_START			// if f2 != 0, jump

# ------------------------------------------
# ------------- END ------------------------
# ------------------------------------------


	bf b0, SWAP_POINTERS			// if b0 == 0, jump
	rfr a7, f0 						// a7 = f0 = p_a1
	rfr a4, f1
	j SWAP_POINTERS_END
SWAP_POINTERS:
	rfr a4, f0
	rfr a7, f1 						// a7 = f1 = p_a2
SWAP_POINTERS_END:


	movi a2, 1
	retw
	.size	nn_asm, .-nn_asm
	.ident	"GCC: (crosstool-NG esp-13.2.0_20230928) 13.2.0"

"""

VALIDATION_C = """
/*
 * validation.c
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
 
#include <stdint.h>
#include <string.h>
#include "validation.h"

{dataset_input_code}

{dataset_output_code}

// **************** User Implementation ****************

#include <stdio.h>
#include "freertos/FreeRTOS.h"

uint32_t t0, t1 = 0;

static void val_print_str(const char *character)
{	
    printf("%s", character);
}

static void val_print_uint16(uint16_t value)
{
    printf("%"PRIu16"", value);
}

static void val_print_uint32(uint32_t value)
{
    printf("%"PRIu32"", value);
}

static uint32_t val_get_cycles()
{
    return esp_cpu_get_cycle_count();
}
// *******************************************************

#define HIST_ERROR_TOTAL 9
#define HIST_ERROR_N4P 0
#define HIST_ERROR_N3 1
#define HIST_ERROR_N2 2
#define HIST_ERROR_N1 3
#define HIST_ERROR_0 4
#define HIST_ERROR_P1 5
#define HIST_ERROR_P2 6
#define HIST_ERROR_P3 7
#define HIST_ERROR_P4P 8

uint16_t histogram[DATASET_LEN][HIST_ERROR_TOTAL] = {};

const char *comma = ", ";
const char *nl = "\\n";
const char *hist_str = "histogram_";
const char *cycles_str = "cycles_";

void val_inference_start()
{
    t0 = val_get_cycles();	
}

void val_inference_end(uint32_t dataset_idx)
{
    t1 = val_get_cycles();

    val_print_str(cycles_str);
    val_print_uint32(dataset_idx);
    val_print_str(comma);
    val_print_uint32(t1 - t0);
    val_print_str(nl);
}

void histogram_add(int32_t error, uint32_t dataset_idx)
{
    // Update histogram
    switch (error) 
    {
        case -3:
            histogram[dataset_idx][HIST_ERROR_N3]++;
            break;
        case -2:
            histogram[dataset_idx][HIST_ERROR_N2]++;
            break;
        case -1:
            histogram[dataset_idx][HIST_ERROR_N1]++;
            break;
        case 0:
            histogram[dataset_idx][HIST_ERROR_0]++;
            break;
        case 1:
            histogram[dataset_idx][HIST_ERROR_P1]++;
            break;
        case 2:
            histogram[dataset_idx][HIST_ERROR_P2]++;
            break;
        case 3:
            histogram[dataset_idx][HIST_ERROR_P3]++;
            break;
        default:
            if(error >= 4)
            {
                histogram[dataset_idx][HIST_ERROR_P4P]++;
            }
            else if (error <= 4)
            {
                histogram[dataset_idx][HIST_ERROR_N4P]++;
            }
            else
            {
                // Unreachable code
            }
            break;						
    }
}

void histogram_show(uint32_t dataset_idx)
{   
    val_print_str(hist_str);
    val_print_uint32(dataset_idx);
    val_print_str(comma);
    val_print_uint16(histogram[dataset_idx][HIST_ERROR_N4P]);
    val_print_str(comma);
    val_print_uint16(histogram[dataset_idx][HIST_ERROR_N3]);
    val_print_str(comma);
    val_print_uint16(histogram[dataset_idx][HIST_ERROR_N2]);
    val_print_str(comma);
    val_print_uint16(histogram[dataset_idx][HIST_ERROR_N1]);
    val_print_str(comma);
    val_print_uint16(histogram[dataset_idx][HIST_ERROR_0]);
    val_print_str(comma);
    val_print_uint16(histogram[dataset_idx][HIST_ERROR_P1]);
    val_print_str(comma);
    val_print_uint16(histogram[dataset_idx][HIST_ERROR_P2]);
    val_print_str(comma);
    val_print_uint16(histogram[dataset_idx][HIST_ERROR_P3]);
    val_print_str(comma);
    val_print_uint16(histogram[dataset_idx][HIST_ERROR_P4P]);
    val_print_str(nl);
    
    memset(histogram, 0, sizeof(histogram));
}

void val_set_input(int8_t **input, uint32_t dataset_idx)
{
    for (uint16_t i = 0; i < DATASET_INPUT_LEN; i++) 
    {
        // Set the input
        (*input)[i] = dataset_inputs[dataset_idx][i];
    }
}

void val_output(int8_t *output, uint32_t dataset_idx)
{
    for (int i = 0; i < DATASET_INPUT_LEN; i++) 
    {    
        // Calculate the error    
        int32_t error = dataset_outputs[dataset_idx][i] - output[i];

        // Add to histogram
        histogram_add(error, dataset_idx);
    }

    // Print the histogram
    histogram_show(dataset_idx);
}

"""

VALIDATION_H = """
/*
 * validation.h
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
 
#ifndef VALIDATION_H
#define VALIDATION_H

#include <stdint.h>

#define DATASET_LEN {dataset_rows}
#define DATASET_INPUT_LEN {dataset_columns}

void val_set_input(int8_t **input, uint32_t dataset_idx);
void val_output(int8_t *output, uint32_t dataset_idx);
void val_inference_start();
void val_inference_end(uint32_t dataset_idx);

#endif  

"""
