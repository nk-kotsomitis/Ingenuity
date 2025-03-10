

#ifndef VALIDATION_H
#define VALIDATION_H

#include <stdint.h>

#define DATASET_LEN 2
#define DATASET_INPUT_LEN 640

void val_set_input(int8_t *input, uint32_t dataset_idx);
void val_output(int8_t *output, uint32_t dataset_idx);
void val_inference_start();
void val_inference_end(uint32_t dataset_idx);

#endif  

