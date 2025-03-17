
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
    // printf("\n\nRes = 0x%"PRIx32"  %"PRId32"\n", res, res); // Debug
	
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
    