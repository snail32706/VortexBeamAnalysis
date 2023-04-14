import numpy as np


class SimulateLIPSS():
    

    '''
    使用 sinfunction & stepfunction 完成 f(r) = LIPSS structure 的 function.
    
    finction 為：
                    f(r) = A*sin(2πk•r + phi) + y0
            
    A       : sinfunction 振幅
    y0      : 平均高度
    delta_y : sinfunc 與 平整處高度差
    k       : wanvenumber
    phi     : 相位
    r1      : 起始點
    r2      : 終點
    
    為了還原實際狀況，增加了剝蝕下淺：
    
                     f(r) = [A*sin(2πk•r + phi) - delta_y] * stepFunction + y0
                     
    以及製造 隨機雜訊 array:
    
    randomRange : 
        每個雜訊元素的值在 -randomRange ~ randomRange 之間。 type = float64
    
    '''

    def __init__(self, A, y0, delta_y, k, phi, r1, r2):
        self.A       = A
        self.y0      = y0
        self.delta_y = delta_y
        self.k       = k
        self.phi     = phi
        self.r1      = r1
        self.r2      = r2
    
    def stepFunction(self, r, R):
        '''
        stepFunction:
            if r < R:
                f(r) = 0
            elif r = R:
                f(r) = 0
            else:
                f(r) = 1
        '''
        return np.heaviside((r - R), 0)

    def sinFunc(self, r, k, phi):
        '''
            f(r) = sin[2πk•r + phi]
        '''
        return np.sin((2*np.pi)*k*r + phi) 

    # def noice(self, row, col, randomRange):
    #     '''
    #     產生一個 row * col 的隨機數陣列，每個元素的值在 -randomRange ~ randomRange 之間
    #     '''
    #     return np.random.rand(row, col) * 2*randomRange - randomRange

    def simulateDonet(self, r):
        
        functionRange = self.stepFunction(r, R=self.r1) - self.stepFunction(r, R=self.r2)
        sin           = self.sinFunc(r, self.k, self.phi)
        
        return (self.A*sin - self.delta_y) * functionRange + self.y0 