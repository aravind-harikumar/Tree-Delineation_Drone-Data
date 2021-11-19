# import rpy2.robjects as robjects
import os
import numpy as np
import subprocess
import pandas as pd

# import rpy2.interactive as r
# from rpy2.robjects.packages import importr

# from ProjectConstants import GlobalConstants as gc
def RunRScript(script_path):
    # return subprocess.check_call(["Rscript"] + list(["/home/ensmingerlabgpu/Documents/Code_Fuzzy/RProgram/FCM-MRF_PYTHON.R"]))
    return subprocess.call("/usr/bin/Rscript --vanilla " + str(script_path), shell=True)
    
# exit(0)

# import subprocess
# RunRScript('/home/ensmingerlabgpu/Documents/Code_Fuzzy/RProgram/FCM-MRF_PYTHON.R')

values = [('DSS/SD','DD','F')]
base_filename = '/home/ensmingerlabgpu/Documents/Code_Fuzzy/RProgram/FCM-MRF_PYTHON.R_Filename.txt'
np.savetxt(base_filename, values, fmt='%s', delimiter=',')
# with open(base_filename, 'a') as f:
#     f.write(
#         aRY.to_string(header = False, index = False)
#     )


# def test():
    
#     base_path = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20180514/Buffer_Crop_Results/Buffer_Ortho_Crop_Results/'
#     out_base = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20180514/ITC-Data/All-ITC/ITC-Crown-Shp/'
#     # date = '20180514'


#     ts=robjects.r('ts')
#     # Input folder path
#     out_buffered_ortho_path = os.path.join(base_path)
#     # FCM out path
#     out_buffered_fcm_path = os.path.join(out_base)
#     # OtherUtils.TouchPath(out_buffered_fcm_path)

#     # Loop through all images in folder and genereate fuzzy maps
#     for root, folders, files in os.walk(out_buffered_ortho_path):
#         for file_name in files:
#             ff = os.path.splitext(os.path.basename(file_name))
            
#             latval = float(ff[0].split('_')[1])
#             longval =  float(ff[0].split('_')[2])

#             imagebands = os.path.join(root, file_name)
#             print(imagebands)

#             outspath = os.path.join(out_buffered_fcm_path,file_name)
#             print(outspath)
#             # exit(0)
#             rstring="""
#                 function(inpath, outpath, latt, long){
                    
#                     require(rgdal)
#                     require(mvtnorm)
#                     require(rgl)
#                     require(scatterplot3d)
#                     require(R.utils)
#                     require(RColorBrewer)

#                     # Read the input image
#                     Path <- ''
#                     str_name <- inpath
#                     imageObj <- readGDAL(paste(Path , "/", str_name, sep=""))
#                     imageObjArray <- as.array(imageObj)
#                     opgd <- GDALinfo(paste(Path , "/", str_name, sep=""))

#                     # Extrat the dimensionality details
#                     imageReadObj <- GDAL.open(paste(Path , "/", str_name, sep=""))
#                     d <- dim(imageReadObj)
#                     Bands <-d[3]
#                     M <- d[2]
#                     N <- d[1]
#                     n <- M*N

#                     # Actual window size is 2*WSize+1
#                     WSize  <- 3

#                     # Max number of neighbours
#                     Nn	<- (WSize*2+1)^2-1

#                     #Fuzzification Factor
#                     m  = 2.2

#                     # number of classes
#                     Ncl <- 2

#                     # The weightage to spatial and spectral components
#                     lambda <- 0.8

#                     # Maximum DN Value
#                     maxDN <- 65536

#                     Neigh_Coord  <- array(0, c(M, N, 4))
#                     Weight		<- array(0, c(2*WSize+1, 2*WSize+1))

#                     # Randomly initialize membership values
#                     MembValArray = array(runif(N*M*Ncl),c(M,N,Ncl))

#                     getRandomMemVal <- function(){
                    
#                     MembValArray1= array(runif(N*M*Ncl),c(M,N,Ncl))
                    
#                     for (i in 1:M)
#                         for (j in 1:N)
#                         MembValArray1[i,j,]= MembValArray1[i,j,]/sum(MembValArray1[i,j,])
                        
#                         return (MembValArray1)
#                     }

#                     # Assign mean values for each class
#                     MeanClassVal <- array(0,c(Bands,Ncl))
#                     # MeanClassVal[,] <- c(c(77,36,88,55), c(75,36,85,50), c(84,42,90,57),c(100,66,66,85), c(70,32,25,15))
#                     # MeanClassVal[,] <- c(c(55306,51578,52770,39886,46205,65535), c(18713,19816,18292,17258,32818,65535), c(5692,4279,6468,8274,15376,65535))
#                     # MeanClassVal[,] <- c(c(55306,51578,52770,39886,46205,65535), c(5692,4279,6468,8274,15376,65535))
#                     #MeanClassVal[,] <- c(c(17701,16377,15707,13685,24597,44535), c(5692,4279,6468,8274,15376,65535))
#                     MeanClassVal[,] <- c(c(1849,2485,1532,1255,10486), c(1,1,1,1,1))

#                     # Function to find initial optimal memebrship values for a specific class and pixel
#                     Uvalues <- function (i,j,cl){
#                     denotmp <- 0
#                     numetmp <- 0
#                     tempOpt <- 0
#                     for (cl1 in 1:Ncl){    
#                         numetmp <- L2dist(i,j,cl) 
#                         if(numetmp == 0)
#                         return (1)
#                         denotmp <- L2dist(i,j,cl1)
#                         tempOpt <- tempOpt + ((numetmp/denotmp)^(2/(m-1)))
#                     }
#                     return((tempOpt)^-1)
#                     }

#                     # Function to find initial optimal memebrship values for all classes and pixels
#                     getAllUValues <- function(){
#                     for (i in 1:M)
#                         for (j in 1:N)
#                         for (cl in 1:Ncl){
#                             MembValArray[i,j,cl] <- Uvalues(i,j,cl)
#                         }
#                     return(MembValArray)
#                     } 

#                     # Function to find initial optimal cluster centers for a specific class
#                     Vvalues <- function (cls){
#                     num <- 0
#                     den <- 0
#                     for (i in 1:M)
#                         for (j in 1:N){
#                         num <- num + ((MembValArray[i,j,cls])^m * imageObjArray[i,j,])
#                         den <- den + (MembValArray[i,j,cls])^m
#                         }
#                     return(num/den)
#                     }

#                     # Function to find initial optimal cluster centers for all classes 
#                     getAllVvalues <- function (){
#                     for (cl in 1: Ncl){
#                         MeanClassVal[,cl] <- Vvalues(cl)
#                     }
#                     return(MeanClassVal)
#                     }

#                     #MeanClassVal[,1] = Vvalues(1)

#                     hist_stretch <- function(data) {
#                     cur.lim<-quantile(data,c(0.025,0.975),na.rm=TRUE)
#                     data<-pmax(cur.lim[1],pmin(cur.lim[2],data))
#                     data<-floor(maxDN*(data-cur.lim[1])/(cur.lim[2]-cur.lim[1]))
#                     data[is.na(data)]<-0
#                     return(data)
#                     }

#                     # Find the L2 norm of a vector
#                     L2dist <- function(rowNo, colNo, classNo){  
#                     #To handle the case when the datavectpr ==  Mean vector 
#                     if(all(imageObjArray[rowNo,colNo,] ==  MeanClassVal[,classNo])){
#                         return (1)  
#                     }
#                     # L2 distnace calculation
#                     dist <-sqrt(sum((imageObjArray[rowNo,colNo,] - MeanClassVal[,classNo])^2))
#                     return(dist)
#                     }

#                     # Find the L2 norm of a vector (a duplicate function made for calculating D in objective function)
#                     L2distObjFunc <- function(rowNo, colNo, classNo){  
#                     dist <-sqrt(sum((imageObjArray[rowNo,colNo,] - MeanClassVal[,classNo])^2))
#                     #imageObjArray
#                     return(dist)
#                     }

#                     FCM <- function(i,j,cl){
#                     totVal <- 0
#                     # for (cl in 1:Ncl)
#                     totVal <- totVal + ((f[i,j,cl])^m)*L2distObjFunc(i,j,cl)
#                     return(totVal)
#                     }



#                     # Function assigning weights in the neighbourhood
#                     Fw <- function(a,b){
                    
#                     val <- a^2 + b^2
#                     val <- 1 / val
#                     #	val <- 1 / sqrt(val)
#                     val <- val^(0.5)
                    
#                     val[val==Inf]<-0
                    
#                     return(val)
#                     }

#                     for(k in 1:(2*WSize+1))
#                     for(l in 1:(2*WSize+1))
#                     {
#                         Weight[k, l] <- Fw(k-(WSize+1),l-(WSize+1))
#                     }

#                     Weight <- Weight/ sum(Weight)

#                     for(i in 1:M)
#                     for(j in 1:N)
#                     {
#                         imin <- i - WSize
#                         imax <- i + WSize
#                         jmin <- j - WSize
#                         jmax <- j + WSize
                        
#                         if(imin<1)  imin <-1
#                         if(imax>M) imax <-M
#                         if(jmin<1)  jmin <-1
#                         if(jmax>N) jmax <-N
                        
#                         Neigh_Coord[i, j, ] <- c(imin,imax,jmin,jmax)
#                     }

#                     Uprior <- function(i,j,cl){
#                     val <- 0
                    
#                     f1 <- f[((Neigh_Coord[i,j,1]):(Neigh_Coord[i,j,2])),((Neigh_Coord[i,j,3]):(Neigh_Coord[i,j,4])),cl]
#                     W1 <- Weight[(Neigh_Coord[i,j,1]-i+1+WSize):(Neigh_Coord[i,j,2]-i+1+WSize),(Neigh_Coord[i,j,3]-j+1+WSize):(Neigh_Coord[i,j,4]-j+1+WSize)]
                    
#                     f0 <- (f1 - f[i,j,cl])^2
#                     #print(dim(f0))
#                     #print(dim(W1))
#                     val <- val + (0.5 * sum(W1 * f0))
#                     return(val)
#                     }

#                     DA3prior <- function(i,j,cl){
#                     val <- 0
                    
#                     f1 <- f[((Neigh_Coord[i,j,1]):(Neigh_Coord[i,j,2])),((Neigh_Coord[i,j,3]):(Neigh_Coord[i,j,4])),cl]
#                     #W1 <- Weight[(Neigh_Coord[i,j,1]-i+1+WSize):(Neigh_Coord[i,j,2]-i+1+WSize),(Neigh_Coord[i,j,3]-j+1+WSize):(Neigh_Coord[i,j,4]-j+1+WSize)]
                    
#                     f0 <- (f1 - f[i,j,cl])^2
                    
#                     for (ct in 1:(dim(f0)[1]*dim(f0)[2])){
#                         val <- val + (gamma * log(1 + ((f0[ct])/gamma)))
#                     }
                    
#                     return(val)
#                     }


#                     U <- function(i,j,clv){
                    
#                     val <-  (1.0-lambda) * FCM(i,j,clv) + lambda * DA3prior(i,j,clv)
#                     return(val)
#                     }


#                     #================================================================================================
#                     # Block 5:  Energy optimisation with simulated annealing
#                     #================================================================================================

#                     # Maximum allowed number of iterations
#                     Niter  <- 1

#                     # SA cooling schedule parameters
#                     T0    <- 3.0
#                     Tupd <- 0.9

#                     # Convergence criterion for SA
#                     min_acc_thr <- 0.1*10^(-2)

#                     Thist  <- array(0, 1)

#                     T <- T0

#                     #par(mfrow=c(1,1))
#                     stop_crit <- 0

#                     f <- array(0,c(M,N,Ncl)) 

#                     F <- MembValArray # imageObjArray
#                     #for(k in 1:Nb)d[,,k] <- as.matrix(D@data[,k],nrow=N,ncol=M,byrow=TRUE) 

#                     f[,,1] <- as.matrix(F[,,1],nrow=N,ncol=M,byrow=TRUE) 
#                     f[,,2] <- as.matrix(F[,,2],nrow=N,ncol=M,byrow=TRUE) 
#                     #f[,,3] <- as.matrix(F[,,3],nrow=N,ncol=M,byrow=TRUE) 
#                     #f[,,4] <- as.matrix(F[,,4],nrow=N,ncol=M,byrow=TRUE)
#                     #f[,,5] <- as.matrix(F[,,5],nrow=N,ncol=M,byrow=TRUE)

#                     Cl_legend <- c("Class1","Class2","Class3","Class4")
#                     Cl_col <- c("lightgreen","lightblue","orange","darkgreen")

#                     gsd <- opgd['res.x']
#                     xyoffset <- c(latt, long)
#                     xyoffset <- xyoffset - opgd['columns']/2*c(gsd,gsd)
#                     #Refdata <- data.frame(as.vector(array(0,c(M,N))))
#                     Refdata <-data.frame(as.vector(imageObjArray[,,1]))
#                     names(Refdata) <- "class"
#                     refgrid <- GridTopology(cellcentre.offset=xyoffset,cellsize=c(gsd,gsd),cells.dim=c(M,N))

#                     Ref <- SpatialGridDataFrame(refgrid, Refdata, proj4string = "+proj=utm +zone=19 +datum=WGS84 +units=m +no_defs +ellps=WGS84
#                                                 +towgs84=0,0,0")

#                     Ref$class <- hist_stretch(Ref$class)

#                     #windows()
#                     #image(Ref, axes=TRUE)

#                     #windows()
#                     MLC <- Ref
#                     MLC$class <- array(0,n)


#                     MLC1 <- Ref
#                     MLC1$class <- array(0,n)

#                     f <- getAllUValues()
#                     MembValArray <- f
#                     #MeanClassVal <- getAllVvalues()
#                     #MembValArray <- getAllUValues()

#                     #getAllUValues()

#                     for(iter in 1:Niter)
#                     {
#                     upd_count <- 0
                    
#                     for(cl in 1:Ncl)
#                         for(i in 1:M)
#                         for(j in 1:N)
#                         {        
#                             f_update <-  MembValArray[i,j,cl]
#                             ft <- f[i,j,cl]
                            
#                             if(f_update!=ft)
#                             {
#                             u1 <- U(i,j,cl)
#                             f[i,j,cl] <- f_update
#                             u2 <- U(i,j,cl)
                            
#                             u1 <- u2-u1
#                             #print(u1)
#                             if(T!=0)
#                             {    
#                                 if(u1>0)
#                                 {              
#                                 f[i,j,cl] <- ft
#                                 }
#                                 else
#                                 {
#                                 u1 <- exp(-u1/T)
#                                 xi <- runif(1, min=0, max=1)
                                
#                                 if(xi>u1)
#                                 {              
#                                     f[i,j,cl] <- ft
#                                 }
#                                 else upd_count<-upd_count+1
#                                 }
#                             }              
#                             }
#                         }
                    
#                     Thist[iter]	<- T
                    
#                     if(upd_count<=min_acc_thr*n*Ncl)
#                     {
#                         stop_crit <- stop_crit +1
#                     }
#                     else stop_crit <- 0
                    
#                     if(stop_crit >=3) break
                    
#                     #T <- T * Tupd
#                     T <- T0/log(2+iter)
                    
#                     MeanClassVal <- getAllVvalues()
#                     MembValArray <- getAllUValues()
                    
#                     #print(upd_count)
                    
#                     #par(mfrow=c(1,2))  
#                     #colors <- brewer.pal(4, "Greys")
#                     #pal <- colorRampPalette(colors)
                    
#                     # for(i in 1:Ncl){
#                     F <- as.vector(f[,,1])
#                     MLC1$class <- round((F/max(F)) * 65536) 
#                     #image(MLC1, col = gray.colors(12),axes=FALSE)
#                     #image(MLC, axes=TRUE)
#                     #title(paste("Iteration ",iter,sep=""))
                    
#                     F <- as.vector(f[,,2])
#                     MLC$class <- round((F/max(F)) * 65536) 
#                     #MLC$class <- (MLC$class > MLC1$class*3.0)*MLC$class
#                     #image(MLC, col = gray.colors(12),axes=FALSE)
#                     #image(MLC, axes=TRUE)
#                     #title(paste("Iteration ",iter,sep=""))
#                     # }  
                    
#                     # MembValArray <- getRandomMemVal()
#                     writeGDAL(MLC, paste(outpath, sep=""))
#                     }

#                 }
#             """
#             rfunc=robjects.r(rstring)

#             rdata = ts(imagebands)
#             rdata2 = ts(outspath)
#             latt = ts(latval)
#             longs = ts(longval)

#             r_df=rfunc(rdata,rdata2,latt,longs)

# test()