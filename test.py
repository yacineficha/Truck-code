import pytorch_ssim
import torch
from torch.autograd import Variable
from time import time

class a():
	def __init__(self):
		pass
	def troll(self):
		self.img1 = Variable(torch.rand(1, 3, 32, 64) + 1).cuda()
		self.img2 = Variable(torch.rand(1, 3, 32, 64) + 2).cuda()
		print(pytorch_ssim.ssim(self.img1, self.img2).cpu().numpy())
	def warmup(self):
        
		img1 = Variable(torch.rand(1, 3, 32, 64))
		img2 = Variable(torch.rand(1, 3, 32, 64))
		if torch.cuda.is_available():
			img1 = img1.cuda()
			img2 = img2.cuda()
		pytorch_ssim.ssim(img1, img2)

b = a()
for i in range(10):
	var = time()
	b.warmup()
	
	print(time()-var)

c = a()
for j in range(5):
	var = time()
	c.warmup()
	
	print(time()-var)

	