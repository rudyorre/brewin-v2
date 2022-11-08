import interpreterv2 as brewin
import sys

def main():
    file = open(sys.argv[1], 'r')
    interpreter = brewin.Interpreter()
    interpreter.run([line for line in file.readlines()])
    file.close()

if __name__ == '__main__':
    main()