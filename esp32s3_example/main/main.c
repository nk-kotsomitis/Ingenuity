

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "freertos/projdefs.h"
#include "validation.h"
#include "../components/nn/include/NN_lite_API.h"

void app_main(void)
{
    NN_lite_res_t res = NN_LITE_ERROR;
    In_out_t input[NN_LITE_INPUT_LENGTH] = {};
    In_out_t *output;
    
    vTaskDelay(pdMS_TO_TICKS(500));
    
    uint32_t inferences_n = 100;
    
    while(inferences_n)
    {
        for(uint32_t dataset_idx = 0; dataset_idx < DATASET_LEN; dataset_idx++)
        {
            // Set validation input
            val_set_input(input, dataset_idx);
    
            // Start cycles counter
            val_inference_start();
    
            // Inference
            res = NN_lite_inference(input, &output);
    
            // Stop cycles counter
            val_inference_end(dataset_idx);
    
            // Set validation output
            val_output(output, dataset_idx);
    
            vTaskDelay(pdMS_TO_TICKS(10));
            
            inferences_n--;
            if(!inferences_n)
            {
                break;
            }
        }
    }
}
