

class VedioType():
    def __init__(self, string):
        self.ROI_xleft  # ROI左邊邊界
        self.ROI_xright # ROI右邊邊界
        self.ROI_ytop   # ROI上面邊邊界
        self.ROI_ydown  # ROI下面邊邊界
        self.SIZE_uplmt # 棒球面積大小上限BALLSIZE_upper_limit
        self.SIZE_lwlmt # 棒球面積大小下限BALLSIZE_lowwer_limit
        self.DIF_wh     # 棒球區域寬高差需小於 "DIF_wh"
        self.LMT_wh     # 棒球區域寬高需小於 "LMT_wh"
        if string == "iphone":
            self.iphone()
            
    def iphone(self):
        self.ROI_xleft = 770
        self.ROI_xright = 1250
        self.ROI_ytop = 50
        self.ROI_ydown = 550
        self.SIZE_uplmt = 1800
        self.SIZE_lwlmt = 270
        self.DIF_wh = 10
        self.LMT_wh = 60 

        