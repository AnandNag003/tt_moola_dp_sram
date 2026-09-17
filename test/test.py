# SPDX-FileCopyrightText: © 2026 Anand Nagaraj
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge


def make_ui(addr: int, en_a: int = 1, we_a: int = 0, en_b: int = 0) -> int:
    """Pack control signals into ui_in[7:0]."""
    return (addr & 0x0F) | ((en_a & 1) << 4) | ((we_a & 1) << 5) | ((en_b & 1) << 6)


@cocotb.test()
async def test_project(dut):
    dut._log.info("Starting Moola DP SRAM Cocotb Test")

    # Start 100 kHz clock (10 us period)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # 1. Apply Reset
    dut._log.info("Applying reset...")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # 2. Write 0xA5 to Address 3 (drive on falling edge)
    await FallingEdge(dut.clk)
    dut._log.info("Writing 0xA5 to address 3")
    dut.ui_in.value = make_ui(addr=3, en_a=1, we_a=1)
    dut.uio_in.value = 0xA5

    # 3. Write 0x5A to Address 7
    await ClockCycles(dut.clk, 1)
    dut._log.info("Writing 0x5A to address 7")
    dut.ui_in.value = make_ui(addr=7, en_a=1, we_a=1)
    dut.uio_in.value = 0x5A

    # 4. Turn off Write-Enable and request Read from Address 3
    await ClockCycles(dut.clk, 1)
    dut._log.info("Requesting read from address 3")
    dut.ui_in.value = make_ui(addr=3, en_a=1, we_a=0)
    dut.uio_in.value = 0x00

    # 5. Wait 1 clock cycle for synchronous memory latency, then check on falling edge
    await ClockCycles(dut.clk, 1)
    await FallingEdge(dut.clk)
    dut._log.info(f"Read back address 3: {hex(int(dut.uo_out.value))}")
    assert dut.uo_out.value == 0xA5, f"Expected 0xA5 at addr 3, got {dut.uo_out.value}"

    # 6. Read from Address 7
    dut.ui_in.value = make_ui(addr=7, en_a=1, we_a=0)
    await ClockCycles(dut.clk, 1)
    await FallingEdge(dut.clk)
    dut._log.info(f"Read back address 7: {hex(int(dut.uo_out.value))}")
    assert dut.uo_out.value == 0x5A, f"Expected 0x5A at addr 7, got {dut.uo_out.value}"

    dut._log.info("All write and read tests passed successfully!")