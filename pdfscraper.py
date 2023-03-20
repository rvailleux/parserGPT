import sys
import getopt
import os
import pypdf

debug = False
fromdirectorypath = ''
todirectorypath = ''

try:
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv,"hi:o:d",["inputdir=", "outputdir=", "debug"])

    requirements = ['-i', '-o']

    for opt, arg in opts:
        if opt == '-h':
            print ('pdfscraper.py -d <path_to_directory>')
            sys.exit()
        elif opt in ("-i", "--inputdir="):
            print("-i option detected : " + arg)
            fromdirectorypath = arg
            requirements.remove("-i")
        elif opt in ("-o", "--outputdir="):
            print("-o option detected : " + arg)
            todirectorypath = arg
            requirements.remove("-o")
        elif opt in ("-d", "--debug"):
            debug=True

    if len(requirements) > 0:
        raise getopt.GetoptError("Lacking mandatory options.")

except getopt.GetoptError as e:
    print (e.msg + ' : pdfscraper.py -i <path_to_input_directory> -o <path_to_input_directory>')
    sys.exit(2)


def logp(msg):
    if debug:
        print(msg)

def crawlDirectory(inputdirectorypath, outputdirectorypath):

    if not os.path.isdir(inputdirectorypath) or not os.path.exists(inputdirectorypath):
        raise FileExistsError(inputdirectorypath + ' is not a path to a directory.')
        
    if not os.path.exists(outputdirectorypath):
        os.mkdir(outputdirectorypath)

    
    # Get all the text files in the text directory
    for file in os.listdir(inputdirectorypath):

        #create file object variable
        #opening method will be rb
        with open(os.path.join(inputdirectorypath,file),'rb') as pdffileobj:
        
            #create reader variable that will read the pdffileobj
            pdfreader=pypdf.PdfReader(pdffileobj)
            
            #This will store the number of pages of this pdf file
            numPages=len(pdfreader.pages)
            pagesread=0

            while pagesread < numPages:

                logp("Reading page " + str(pagesread))
                
                #create a variable that will select the page
                pageobj=pdfreader.pages[pagesread]
                
                #(x+1) because python indentation starts with 0.
                #create text variable which will store all text datafrom pdf file
                text=pageobj.extract_text()

                logp(text)
                
                #save the extracted data from pdf to a txt file
                #we will use file handling here
                #dont forget to put r before you put the file path
                #go to the file location copy the path by right clicking on the file
                #click properties and copy the location path and paste it here.
                #put "\\your_txtfilename"
                file1=open(os.path.join(outputdirectorypath,str(hash(pdffileobj.name))+".txt"),"a")
                file1.writelines(text)

                pagesread += 1



crawlDirectory(fromdirectorypath, todirectorypath)