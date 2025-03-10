
# a1 + 16: arg1 - a2 - pointer_sm 
# a1 + 20: arg2 - a3 - pointer_zf
# a1 + 24: arg3 - a4 - pointer_a1
# a1 + 28: arg4 - a5 - pointer_w
# a1 + 32: arg5 - a6 - pointer_b
# a1 + 36: arg6 - a7 - pointer_a2

	.text
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
	addi  a1, a1, -16		

	l32i  a9,  a3, 12		// a14  = y_mul_0
	s32i  a9,  a1, 0

	l32i  a9,  a3, 16		// a14  = y_mul_1
	s32i  a9,  a1, 4

	l32i  a9,  a3, 20		// a14  = y_mul_2
	s32i  a9,  a1, 8

	l32i  a9,  a3, 24		// a14  = y_mul_3
	s32i  a9,  a1, 12

	addi   a3, a3, 28		// pointer_zf += 7
	#addi   a3, a3, 1024		// pointer_zf += 256
# ------------------------------------------
# ------------- 1.Multiplication -----------
# ------------------------------------------

ST_MATRIX_START:
	ee.zero.accx						// accx = 0
	wfr f8, a4
	#mov a8, a4							// a8 = a4 = pointer_a1
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
	l32i a8, a1, 0		// load y_mul_0
	mull a12, a15, a8	// mull


	# ******* res = acc * y_mul_1 *******
	extui  a9, a14, 0, 8	// a9 = y1
	ssr	   a9				// SAR = y1
	sra    a15, a15			// a9 = acc >> y1

	l32i  a8, a1, 4			// load y_mul_1
	mull  a9, a15, a8		// mull
	add a12, a12, a9		// a12 += a8


	# ******* res = acc * y_mul_2 *******
	extui  a9, a14, 8, 8	// a9 = y1
	ssr	   a9				// SAR = y1
	sra    a15, a15			// a9 = acc >> y1


	l32i  a8, a1, 8			// load y_mul_3
	mull  a9, a15, a8		// mull
	add a12, a12, a9		// a12 += a8


	# ******* res = acc * y_mul_3 *******
	extui  a9, a14, 16, 8	// a9 = y1
	ssr	   a9				// SAR = y1
	sra    a15, a15			// a9 = acc >> y1

	l32i  a8, a1, 12		// load y_mul_1
	mull  a9, a15, a8		// mull
	add a12, a12, a9		// a12 += a8

j DEQUANTIZATION_Y_MAX
	# ********** Negative ACC ********************
DEQUANTIZATION_NEGATIVE_ACC:

	# ******* res = acc * y_mul_0 *******
	movi   a12, 0		// res
	l32i a8, a1, 0		// load y_mul_0
	mull a12, a15, a8	// mull


	# ******* res = acc * y_mul_1 *******
	extui  a9, a14, 0, 8	// a9 = y1
	ssr	   a9				// SAR = y1
	neg    a15, a15
	sra    a15, a15			// a9 = acc >> y1
	neg    a15, a15

	l32i  a8, a1, 4			// load y_mul_1
	mull  a9, a15, a8		// mull
	add a12, a12, a9		// a12 += a8


	# ******* res = acc * y_mul_2 *******
	extui  a9, a14, 8, 8	// a9 = y1
	ssr	   a9				// SAR = y1
	neg    a15, a15
	sra    a15, a15			// a9 = acc >> y1
	neg    a15, a15


	l32i  a8, a1, 8			// load y_mul_3
	mull  a9, a15, a8		// mull
	add a12, a12, a9		// a12 += a8


	# ******* res = acc * y_mul_3 *******
	extui  a9, a14, 16, 8	// a9 = y1
	ssr	   a9				// SAR = y1
	neg    a15, a15
	sra    a15, a15			// a9 = acc >> y1
	neg    a15, a15

	l32i  a8, a1, 12		// load y_mul_1
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
	neg  a15, a12


DEQUANTIZATION_ZERO_POINT:
	#extui a9,  a13, 24, 8	// a9 = zero_point_a2
	#srai a9, a13, 24		// a9 = zero_point_a2 NOTE: Arithmetic shift is required to preserve sign
	rfr a9, f11
	add  a15, a15, a9		// a15 = acc + zero_point_a2


	rfr a12, f9 // accum
	beqz a12, LUT_END

#j LUT_END

LUT:
	addi a13, a15, 128		// idx = res + 128 [0 - 255]
    slli a13, a13, 2        // idx * 4 bytes

	add a3, a3, a13			// a3 = a3 + idx
	l32i a9, a3, 0
	neg a13, a13
	add a3, a3, a13

    // if (accum >= acc_limit)
    // if (acc_limit < accum)
	rfr a12, f9					// a12 = accum
	
	
    
    #bge a12, a9, LUT_END
	
	blt a12, a9, LUT_END		// a12 = accum, a9 = limit,   if (accum >= limit)  res++
    addi a15, a15, 1 // res++
LUT_END:

	# Clipping
#j DEQUANTIZATION_END
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
	addi  a1, a1, 16				

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

