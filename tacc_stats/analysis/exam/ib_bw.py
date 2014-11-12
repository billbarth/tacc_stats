from exams import Test
import numpy
from scipy.stats import tmean

class IBBW(Test):

  k1=['ib_sw', 'ib_sw', 'lnet', 'lnet']
  k2=['rx_bytes', 'tx_bytes', 'rx_bytes', 'tx_bytes']

  # If metric is less than threshold then flag 
  comp_operator = '<'
  peak=1.4e10
  
  def compute_metric(self):

    ibbw = 0

    schema_ib = self.ts.j.get_schema('ib_sw')
    schema_lnet = self.ts.j.get_schema('lnet')
    if 'ERROR' in schema_ib or 'ERROR' in schema_lnet: return
    data_ib = self.ts.j.aggregate_stats('ib_sw')
    data_lnet=self.ts.j.aggregate_stats('lnet')
    nodes = data_ib[1]
    data_ib = data_ib[0].astype(float)
    data_lnet = data_lnet[0].astype(float)

    dt=numpy.diff(self.ts.t) 
    ibbw = ((numpy.diff(data_ib[:,schema_ib['tx_bytes'].index]) +
            numpy.diff(data_ib[:,schema_ib['rx_bytes'].index])) -
            (numpy.diff(data_lnet[:,schema_lnet['tx_bytes'].index]) +
            numpy.diff(data_lnet[:,schema_lnet['rx_bytes'].index])) )/dt

    self.metric = tmean(ibbw)/self.peak/self.ts.numhosts

    return


    
