#!/bin/bash
#SBATCH -J pumgen
#SBATCH -o ./%j.%x.out
#SBATCH -e ./%j.%x.out
#SBATCH --mail-type=END
#SBATCH --mail-user=bli@geophysik.uni-muenchen.de
#SBATCH --time=8:30:00
#SBATCH --ear=off
#SBATCH --no-requeue
#SBATCH --export=ALL
#SBATCH --account=pn68fi
#SBATCH --partition=fat
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=16
#SBATCH --cpus-per-task=1
#Needs specific MPI
#Run the program: 
export MP_SINGLE_THREAD=yes

#4*8 CPU for large mesh

prefix=Model_C
# note that I used 2 *32 on fat for the 500mio mesh (3h)

# 0.25Hz-4 wavelengths adds 5mio cells for sulawesi


prefixXml=ModelC_rotatecheck_new

xml=${prefixXml}.xml
cat ${prefixXml}.xml
ulimit -c unlimited
#srun /hppfs/work/pr63qo/di73yeq4/myLibs/PUMGen/build/pumgen -s simmodsuite -l SimModelerLib.lic --analyseAR --xml $xml --sim_log simlog_${prefixXml}.dat  $prefix.smd ${prefixXml} -f attributes,geomsim_discrete,geomsim_discretemodeling,meshsim_surface,meshsim_volume,meshsim_parallelmeshing,attributes
srun /hppfs/work/pr63qo/di73yeq4/myLibs/PUMGen/build/pumgen -s simmodsuite -l SimModelerLib.lic --analyseAR --xml $xml --sim_log simlog_${prefixXml}.dat  $prefix.smd ${prefixXml}
