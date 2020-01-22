"""
/*
 * Copyright (c) P. Arun Babu (www.linkedin.com/in/parunbabu)
 *
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */
"""

import os
import re
import sys
import random

### Mutation tricks ###

NULL_STRING = " "

mutation_trick = {
	" < ": [ " != ", " > ", " <= ", " >= ", " == " ],
	" > ": [ " != ", " < ", " <= ", " >= ", " == " ],
	" <= ": [ " != ", " < ", " > ", " >= ",  "==" ],
	" >= ": [ " != ", " < ", " <= ", " > ",  "==" ],
	" == ": [ " != ", " = ", " < ",  " > ", " <= ", " >= " ],
	" == ": [ " != ", " = ", " < ",  " > ", " <= ", " >= " ],
	" != ": [ " == ", " = ", " < ",  " > ", " <= ", " >= " ],
	" = ": [ " == ", " != ", " < ",  " > ", " <= ", " >= ", " = 0 * ", " = 0 ;//", " = NULL; //", " = ! " ],

	" + ": [ " - ", " * ", " / ", " % " ],
	" - ": [ " + ", " * ", " / ", " % " ],
	" * ": [ " + ", " - ", " / ", " % " ],

	" / ": [ " % ", " * ", " + ", " - " ],
 	" % ": [ " / ", " + ", " - ", " * " ],

	" + 1": [ " - 1", " + 0", " + 2", " - 2" ],
	" - 1": [ " + 1", " + 0", " + 2", " - 2" ],

	" & ": [ " | ", " ^ " ],
	" | ": [ " & ", " ^ " ],
	" ^ ": [ " & ", " | " ],

	" &= ": [ " |= ", " ^= " ],
	" |= ": [ " &= ", " ^= " ],
	" ^= ": [ " &= ", " |= " ],

	"~": [ "!", NULL_STRING ],
	"!": [ "~", NULL_STRING ],

	" && ": [ " & ", " || "," && !" ],

	" || ": [ " | ", " && ", " || !" ],

	" >> ": [ " << " ],
	" << ": [ " >> " ],

	" << 1": [ " << 0", " << -1", " << 2" ],
	" >> 1": [ " >> 0", " >> -1", " >> 2" ],

	"++": [ "--" ],
	"--": [ "++" ],

	"++;": [ "--;", "+=2;", "-=2;" ],
	"++)": [ "--)", "+=2)", "-=2)" ],
	"--;": [ "++;", "+=2;", "-=2;" ],
	"--)": [ "++)", "+=2)", "-=2)" ],

	" true ":  [ " false " ],
	" false ": [ " true " ],

	"if (": [ "if ( ! ", "if ( ~ ", "if ( 1 || ", "if ( 0 && " ],
	"while (": [ "while ( ! ", "while ( ~ ", "while ( 0 && " , "// while (", " if (", "if (!"],
	
	"break;": [ "{;}" ],
	"continue;": [ "{;}" ],
	"goto ": [ "//goto " ],

	"return ": [ "return 0; //", "return 1; //", "return NULL; //", "return -1; //", "return 2* ", "return -1 * " ],


	# for embedded systems

	"0x00": [ "0x01", "0x05", "0x0A", "0x0F", "0xAA", "0x55", "0xFF" ],
	"0x01 ": [ "0x00 ", "0x05 ", "0x0A ", "0x0F " ],
	"0x05 ": [ "0x00 ", "0x01 ", "0x0A ", "0x0F " ],
	"0x0A ": [ "0x00 ", "0x01 ", "0x05 ", "0x0F " ],
	"0x0F ": [ "0x00 ", "0x01 ", "0x05 ", "0x0A " ],

	"0x55 ": [ "0x00 ", "0xAA ", "0xFF " ],
	"0xAA ": [ "0x00 ", "0x55 ", "0xFF " ],
	"0xFF ": [ "0x00 ", "0x55 ", "0xAA " ],
	"[": [ "[ -1 + ", "[ 1 + ", "[ 0 * " ],

	"(": [ " (! " ],

	");": [ "*0);", "*-1);", "*2);" ],
	",": [ ", ! ", ", 0 * ", ", -1 * ", ", 2 *" ],
	" ? ": [ " && 0 ? ", " || 1 ? " ],
	" int ": [" short int ", " char " ],
	" signed ": [ " unsigned " ],
	" unsigned ": [ " signed " ],
	" long ": [ " int ", " short int ", " char " ],
	" float ": [ " int " ],
	" double ": [ " int " ],

	" free(": [ "// free(" ],

	"case ": [ "// case " ],
	"default ": [ "// default " ],

	# null terminate a string
	"\"": [ "\"\\0" ],

	"else {": [ "{" ],
	"else": [ "// else" ],
}

def main (input_file, output_folder):
	output_num = 0

	source_code = open(input_file).read().split('\n')
	number_of_lines_of_code = len(source_code) 

	mutant_operators = mutation_trick.keys()

	mutated_line = ""
	for line in xrange(0,number_of_lines_of_code):
		# do not mutate preprocessor or assert statements
		if source_code[line].strip().startswith("#") or source_code[line].strip().startswith("assert"):
			continue

		for m in mutant_operators:
			mutate_at_index = -1
			# search for substrings we can mutate
			for substring_i in xrange(0, source_code[line].count(m)):
				mutate_at_index = source_code[line].index(m, mutate_at_index + 1)

				for mutate_with in mutation_trick[m]:
					output_num += 1
					output_file = "%s/gen-%05d.c" % (output_folder, output_num)
					sys.stdout.write("\nOutput written to "+output_file+"\n")
	
					sys.stdout.write("Line: "+str(line+1)+"\n")
					sys.stdout.write("Original Line : "+source_code[line].strip()+"\n")
	
					mutated_line = source_code[line][0:mutate_at_index] + source_code[line][mutate_at_index:].replace(m,mutate_with,1)
	
					sys.stdout.write("After Mutation: "+mutated_line.strip()+"\n")
	
					write_to_file(output_file, source_code, line, mutated_line)

	if output_num == 0:
		sys.stderr.write("Could not create a mutant. Please make sure it is a C file.\n")
		sys.stderr.write("You may need to indent your C file.\n")
		exit(1)

def write_to_file ( mutant_file_name, source_code, mutated_line_number, mutated_line ):
	output_file = open(mutant_file_name, "w")

	for line in xrange(0,len(source_code)):
		if line == mutated_line_number: 
			output_file.write("/* XXX: original code was : "+source_code[line]+" */\n")
			output_file.write(mutated_line+"\n")
		else:
			output_file.write(source_code[line]+"\n")

	output_file.close()

if __name__ == "__main__":
	if len(sys.argv) == 3:
		main(sys.argv[1],sys.argv[2]) 

	else:
		sys.stderr.write("Usage: python mutate.py <file-to-mutate.c> [output-folder]\n")
