
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

#define DATASET_LEN 10
#define DATASET_INPUT_LEN 640

void val_set_input(int8_t **input, uint32_t dataset_idx);
void val_output(int8_t *output, uint32_t dataset_idx);
void val_inference_start();
void val_inference_end(uint32_t dataset_idx);

#endif  

