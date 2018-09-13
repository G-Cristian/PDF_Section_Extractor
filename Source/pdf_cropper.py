import sys
import os
from pdf2image import convert_from_path
from PIL import Image
from fpdf import FPDF

def generatePDF():
	pdfCropper = createPDFCropper()
	pdfCropper.generatePDF()

def createPDFCropper():
	if len(sys.argv) < 4:
		print('Invalid args: should be "InputFileName.pdf" "OutputFileName.pdf" CropsList')
		print('where: ')
		print('InputFileName.pdf is the name of the pdf to extract the crops from')
		print('OutputFileName.pdf is the name of the generated pdf with the extracted images')
		print('CropsList is the list of crops to use for extracting the images from the input pdf')
		print('    Example of a list with three crops: "(x1,y1,x2,y2)" "(x1,y1,x2,y2)" "(x1,y1,x2,y2)"')
		print('    where: ')
		print('    x1,y1 is the top-left corner of the crop')
		print('    x2,y2 is the bottom-right corner of the crop')

		exit(1)

	return PDFCropper(sys.argv[1], sys.argv[3:len(sys.argv)] ,sys.argv[2])

class PDFCropper(object):

	tempImagesFolder = "tempImages"
	tempCroppedImagesFolder = "tempCroppedImages"

	def __init__(self, inputFileName, cropsAsStringList=[], outputFileName = "output.pdf"):
		self.inputFileName = inputFileName
		self.crops = self.getCrops(cropsAsStringList)
		self.outputFileName = outputFileName

	def getFilesInFolder(self, folder):
		elements = []
		try:
			elements = os.listdir(folder)
		finally:
			return elements

	def generatePDF(self):
		self.extractPages(self.inputFileName)
		images = self.getImagesFromFolder(PDFCropper.tempImagesFolder)
		croppedImages = self.getCroppedImages(self.crops, images)
		self.saveImages(croppedImages)
		self.createPDF()


	def getCrops(self, cropsAsStringList):
		cropsTuples = []
		crops = []
		for arg in cropsAsStringList:
			crops.append(arg)

		for crop in crops:
			n = len(crop)
			coords = crop[1:n-1].split(',')
			coordsNumbers = []
			for coord in coords:
				coordsNumbers.append(int(coord))
			cropsTuples.append(tuple(coordsNumbers))

		return cropsTuples

	def removeFolderAndFiles(self,folder):
		elements = self.getFilesInFolder(folder)
		for e in elements:
			os.remove(folder+"/{}".format(e))
		try:
			os.rmdir(folder)
		finally:
			return

	def createFolderAndRemoveIfExists(self,folderName):
		self.removeFolderAndFiles(folderName)
		os.mkdir(folderName)


	def extractPages(self,fileName):
		self.createFolderAndRemoveIfExists(PDFCropper.tempImagesFolder)
		pages = convert_from_path(fileName)
		i = 1
		for page in pages:
			page.save(PDFCropper.tempImagesFolder+"/{}.jpg".format(i))
			i = i + 1

	def getImagesFromFolder(self,folderPath):
		n = len(os.listdir(folderPath))
		images = [Image.open(folderPath+"/{}.jpg".format(i)) for i in range(1,n+1)]
		return images

	def getCroppedImages(self,crops, images):
		croppedImages = []
		for img in images:
			for crop in crops:
				croppedImages.append(img.crop(crop))
		return croppedImages

	def saveImages(self,images):
		self.createFolderAndRemoveIfExists(PDFCropper.tempCroppedImagesFolder)
		i = 1
		for image in images:
			image.save(PDFCropper.tempCroppedImagesFolder+"/{}.jpg".format(i))
			i = i + 1

	def createPDF(self):
		pdf = FPDF()
		elements = self.getFilesInFolder(PDFCropper.tempCroppedImagesFolder)

		i = 1
		for element in elements:
			pdf.add_page("L")
			pdf.image(PDFCropper.tempCroppedImagesFolder + "/{}.jpg".format(i))
			i = i + 1

		pdf.output(self.outputFileName, "F")