#Return your program output here for grading (can treat this function as your "main")
def project4(input: str) -> str:
    return ""

def read_file_contents(filepath):
    with open(filepath, "r") as f:
        return f.read() 

#Use this to run and debug code within VS
if __name__ == "__main__":
    input_contents = read_file_contents("Path to input file goes here")
    print(project4(input_contents))
