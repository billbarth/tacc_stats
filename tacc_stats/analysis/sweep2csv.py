#!/usr/bin/env python
from __future__ import print_function
import sys,os,pwd,re
import operator
from datetime import datetime,timedelta
import tacc_stats.analysis.exam as exam
import tacc_stats.analysis.plot as plot
import tacc_stats.cfg as cfg
from tacc_stats.analysis.gen import tspl,tspl_utils
from collections import defaultdict

os.environ['DJANGO_SETTINGS_MODULE']='tacc_stats.site.tacc_stats_site.settings'
sys.path.append(os.environ["HOME"]+"/.local")

from tacc_stats.site.stampede.models import Job

def get_executable(jobid):
    job = Job.objects.get(id=jobid)
    return job.exe

def replace_name(exe,regex_dict):
    for reg in regex_dict.keys():
        if re.match(reg,exe):
            return re.sub(reg+'.*',regex_dict[reg],exe)
    return exe        

# Generate list of files for a date range and test them
def get_filelist(start,end,pickles_dir=None):
    try:
        start = datetime.strptime(start,"%Y-%m-%d")
        end   = datetime.strptime(end,"%Y-%m-%d")
    except:
        start = datetime.now() - timedelta(days=1)
        end   = start

    filelist = []
    for root,dirnames,filenames in os.walk(pickles_dir):
        for directory in dirnames:
            date = datetime.strptime(directory,'%Y-%m-%d')
            if max(date.date(),start.date()) > min(date.date(),end.date()): 
                continue
            print('for date',date.date())
            filelist.extend(tspl_utils.getfilelist(os.path.join(root,directory)))
        break
    return filelist


def main(**args):

    equiv_patterns = {
        r'^charmrun' : 'NAMD*',
        r'^wrf' : 'WRF*',
        r'^vasp' : 'VASP*',
        r'^lmp_' : 'LAMMPS*',
        r'^mdrun' : 'Gromacs*',
        r'^dlpoly' : 'DL_POLY*',
        r'^su3_' : 'MILC*',
        r'^namd2' : 'NAMD*',
        r'^pmemd' : 'Amber*',
        r'^sander' : 'Amber*',
        r'^charmm' : 'CHARMM*',
        r'^c37b1'  : 'CHARMM*',
        r'^arps_mpi' : 'ARPS*', 
        r'^OpenSeesSP' : 'OpenSees*',
        r'^xspecfem3D' : 'SpecFEM3D*',
        r'^parsec.mpi' : 'PARSEC*',
        r'^sm_chroma' : 'Chroma*',
        r'^mitgcmuv' : 'MITGCM*', 
        r'^padcirc' : 'ADCIRC*',
        r'^chroma_laph_lex_3d' : 'Chroma*', 
        r'^flash4' : 'Flash4*',
        r'^siesta' : 'Siesta*', 
        }

    execs = [re.compile(x) for x in equiv_patterns.keys()]


    print(args)
    # Stage exams
    aud = exam.Auditor(processes=args['p'])
    for test in args['test']:
        test_type = getattr(sys.modules[exam.__name__],test)    
        aud.stage(test_type,
                  min_time=args['s'], min_hosts=args['N'],
                  waynesses=args['waynesses'], aggregate=args['a'],
                  ignore_status=args['ignore_status'])

        print('Staging test: '+ test_type.__name__)

    # Compute metrics for exams
    filelist=get_filelist(args['start'],
                         args['end'],
                         pickles_dir = args['dir'])
    aud.run(filelist)

    my_results=defaultdict(dict)
    header='Jobid,'
    for test in args['test']:
        header+=test+','
        for job in aud.metrics[test].keys():
            if aud.metrics[test][job]:
                my_results[job][test]=aud.metrics[test][job]

    print(header+'Executable')
    for job in my_results.keys():
        exe=get_executable(job)
        if exe and any(regex.match(exe) for regex in execs):
            print(job+',', end="")
            for test in args['test']:
                try:
                    print(str(my_results[job][test])+',',end='')
                except KeyError:
                    print(str(-1)+',',end='')
            print(replace_name(exe,equiv_patterns))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run tests for jobs')
    parser.add_argument('-dir', help='Pickles Directory',
                        type=str, default=cfg.pickles_dir)
    parser.add_argument('start', help='Start date',
                        type=str,default='')
    parser.add_argument('end', help='End date',
                        type=str,default='')
    parser.add_argument('-p', help='Set number of processes',
                        type=int, default=1)
    parser.add_argument('-N', help='Set minimum number of hosts',
                        type=int, default=1)
    parser.add_argument('-s', help='Set minimum time in seconds',
                        type=int, default=3600)
    parser.add_argument('-t', help='Set test threshold',
                        type=float, nargs='*',default=[1.0])
    parser.add_argument('-test', help='Test to run',
                        type=str, nargs = '*', default=['Idle'])
    parser.add_argument('-ignore_status', help='Status types to ignore',
                        nargs='*', type=str, default=[])
    parser.add_argument('-waynesses', help='Wayness required',
                        nargs='*', type=int, default=[x+1 for x in range(32)])
    parser.add_argument('-a', help='Aggregate over node', default=True)
    parser.add_argument('-o', help='Output directory',
                        type=str, default='.', metavar='output_dir')
    parser.add_argument('-wide', help='Set wide plot format',
                        action="store_true")
    parser.add_argument('-plot', help='Generate a plot',
                        action="store_true")
    
    main(**vars(parser.parse_args()))
