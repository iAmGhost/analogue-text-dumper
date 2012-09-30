import argparse
import re
import os
import textwrap
import sys

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    #alist.sort(key=natural_keys) sorts in human order
    #http://nedbatchelder.com/blog/200712/human_sorting.html
    return [ atoi(c) for c in re.split('(\d+)', text) ]
	
def dumpBlock(filePath, stripControlCode=True):
	result = ""
	
	file = open(filePath)
	for line in file:
		line = line.replace("\\\"", "{QUOTE}")
		m = re.search("tl_message \"(.*?)\" \".*?\" \"(.*?)\" \"(.*?)\" \"(.*?)\" \"(.*)\"", line)

		if m:
			content = m.group(5).replace("\\n", "\n")
			content = content.replace("\" \"", "\n[Next Page]\n")
			content = content.replace("{QUOTE}", "\"")
			
			if stripControlCode:
				content = re.sub("\{.*?\}", "", content)
				
			result += "%s\n%s\n%s\n%s\n%s\n\n" % (m.group(1), m.group(2), m.group(3), m.group(4), content)
			
	return result

def dumpRpt(filePath, stripControlCode=True, dumpOriginal=False):
	result = ""
	
	file = open(filePath, "r")

	for line in file:
		foundLine = False
		
		char = line[0]
		
		if not dumpOriginal and (char == ">" or char == "^"):
			foundLine = True
		elif dumpOriginal and char == "<":
			foundLine = True
		
		if foundLine:
			line = line[2:].replace("\\n", "\n")
			if stripControlCode:
				line = re.sub("\{.*?\}", "", line)
			
			result += line

	return result
	
def blockDumper(args):
	fileNames = []
	
	for fileName in os.listdir("."):
		if re.match(re.compile(args.infile.replace("#", "\\d+")), fileName):
			fileNames.append(fileName)

	fileNames.sort(key=natural_keys)
	
	outFile = open(args.outfile, "w")
	
	for fileName in fileNames:
		outFile.write(dumpBlock(fileName, args.dont_strip_control_codes))
	
	print "%d files are processed." % len(fileNames)
	print "Dumped texts are saved to: %s" % args.outfile

def rptDumper(args):
	outFile = open(args.outfile, "w")
	
	outFile.write(dumpRpt(args.infile, args.dont_strip_control_codes, args.original_string))
	
	print "Dumped texts are saved to: %s" % args.outfile
	
def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent(
	'''
	Analogue: A Hate Story Text Dumper
	http://iamghost.kr
	'''))
	
	subparsers = parser.add_subparsers(title="modes", help="dumper modes")
	
	parser_blockdump = subparsers.add_parser("blockdump", description="Dump block.rpy files to readable plain text")
	parser_blockdump.add_argument("infile", metavar="infile", type=str, help="Block file name, use # as number wildcard for multiple files\n(block#.rpy will match block1.rpy, block2.rpy and more.)")
	parser_blockdump.add_argument("outfile", metavar="outfile", type=str, help="Result will be stored in this file")
	parser_blockdump.add_argument("-s", "--dont-strip-control-codes", action="store_false", default=True, help="Will not strip control codes if this flag was set.")
	parser_blockdump.set_defaults(func=blockDumper)
	
	parser_rptdump = subparsers.add_parser("rptdump", description="Dump rpt text to readable text")
	parser_rptdump.add_argument("infile", metavar="infile", type=str, help="input file (ex: korean.rpt)")
	parser_rptdump.add_argument("outfile", metavar="outfile", type=str, help="Result will be stored in this file")
	parser_rptdump.add_argument("-o", "--original-string", action="store_true", default=False, help="Dump original strings instead of translations.")
	parser_rptdump.add_argument("-s", "--dont-strip-control-codes", action="store_false", default=True, help="Will not strip control codes if this flag was set.")
	parser_rptdump.set_defaults(func=rptDumper)
	
	if len(sys.argv) == 1:
		parser.print_help()
		return 1
		
	args = parser.parse_args(sys.argv[1:])
	args.func(args)
	
	
if __name__ == "__main__":
	exit(main())