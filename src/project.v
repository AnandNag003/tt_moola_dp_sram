/*
 * Copyright (c) 2026 Anand Nagaraj
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_moola_sram (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered
    input  wire       clk,      // clock
    input  wire       rst_n     // active-low reset
);

  // Synchronous active-high reset for internal logic
  wire rst = !rst_n;

  // Set bidirectional pins purely as inputs to feed Port A write data
  assign uio_oe  = 8'b0000_0000;
  assign uio_out = 8'b0000_0000;

  // Decode control and address from ui_in
  wire [3:0] addr_a = ui_in[3:0]; // 16 words (addresses 0 to 15)
  wire       en_a   = ui_in[4];    // Port A enable
  wire       we_a   = ui_in[5];    // Port A write-enable (wstrb)
  wire       en_b   = ui_in[6];    // Port B enable

  // Data buses
  wire [7:0] wdata_a = uio_in;
  wire [7:0] rdata_a;
  wire [7:0] rdata_b;

  // Drive output pins with Port A read data
  assign uo_out = rdata_a;

  // Instantiate the scaled-down moola_dp_sram (16 words x 8 bits)
  moola_dp_sram #(
      .DATA_WIDTH(8),
      .ADDR_WIDTH(4),
      .BYTE_WIDTH(8),
      .NUM_BYTES(1),
      .INIT_FILE_EN(0)
  ) u_sram (
      // Port A (Read / Write)
      .clk_a   (clk),
      .rst_a   (rst),
      .en_a    (en_a),
      .wstrb_a (we_a),
      .addr_a  (addr_a),
      .wdata_a (wdata_a),
      .rdata_a (rdata_a),

      // Port B (Tied off to avoid floating inputs)
      .clk_b   (clk),
      .rst_b   (rst),
      .en_b    (en_b),
      .wstrb_b (1'b0),
      .addr_b  (addr_a),
      .wdata_b (8'h00),
      .rdata_b (rdata_b)
  );

  // Suppress unused signal warnings cleanly
  wire _unused = &{ena, ui_in[7], rdata_b, 1'b0};

endmodule