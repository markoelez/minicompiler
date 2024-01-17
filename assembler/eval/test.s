// Assembler program to print "Hello World!" to stdout on macOS ARM64 architecture.
// X0-X2 - parameters to Unix system calls
// X16 - Mach System Call function number

.global _start   // Declare the global entry point for the linker
.align 2         // Ensure that the following code is aligned on a 2-byte boundary

// Entry point of the program
_start:
    // Prepare for the write syscall to print a string
    mov     X0, #1             // Set X0 to 1: file descriptor 1 (stdout)
    adr     X1, data           // Load the address of the data section into X1
    mov     X2, #38            // Set X2 to 38: length of the string to be printed
    mov     X16, #4            // Set X16 to 4: syscall number for write operation
    svc     #0x80              // Make a syscall: this line asks the kernel to perform the write

    // Prepare for the exit syscall to terminate the program
    mov     X0, #0             // Set X0 to 0: use 0 as the return code
    mov     X16, #1            // Set X16 to 1: syscall number for exit operation
    svc     #0x80              // Make a syscall: this line asks the kernel to terminate the program

// Data section of the program
data:      
    .ascii  "Hello, world! Everything is working!"
