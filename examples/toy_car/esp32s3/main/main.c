
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
    
    uint32_t inferences_n = 10;
    
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
    
            vTaskDelay(pdMS_TO_TICKS(50));
            
            inferences_n--;
            if(!inferences_n)
            {
                break;
            }
        }
    }
}
