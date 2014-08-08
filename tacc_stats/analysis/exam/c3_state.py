from exams import Test

class C3State(Test):
    k1 = ['intel_snb', 'intel_snb','intel_snb_pcu']      
    k2 = ['CLOCKS_UNHALTED_REF','ERROR','C3_CYCLES']
    comp_operator = '>'
    
    def compute_metric(self):
        print self.ts.j.id
        c3 = self.arc(self.ts.data[2])
        schema = self.ts.j.schemas['intel_snb'].keys()
        if c3 > 0 and 'ERROR' in schema: print '>>>>>>C3 =',c3,self.ts.j.id,schema
        self.metric=c3
