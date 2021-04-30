#include "mpi.h"
#include <stdio.h>
#define  MAX_PROC 128

int NODEID, NNODES;

unsigned char CheckByte(c, n)
    unsigned char *c;
    long n;
{
  unsigned int sum = 0;
  unsigned int mask = 0xff;

  while (n-- > 0)
    sum += (int) *c++;

  sum = (sum + (sum>>8) + (sum>>16) + (sum>>24)) & mask;
  return (unsigned char) sum;
}



/*\ Error handler
\*/
void Error(string, code)
     char *string;
     long code;
{

  (void) fflush(stdout);
  (void) fflush(stderr);

  (void) fprintf(stderr, "%3d:%s %ld(%x)\n", NODEID, string, code, code);
  (void) perror("system message");

  (void) fflush(stdout);
  (void) fflush(stderr);

  MPI_Abort(MPI_COMM_WORLD,code);
}



void SND_(type, buf, lenbuf, node, sync)
     long *type;
     char *buf;
     long *lenbuf;
     long *node;
     long *sync;
{
int ttype = (int)*type;

    MPI_Send(buf, (int)*lenbuf, MPI_CHAR, (int)*node, ttype,MPI_COMM_WORLD);
}


void RCV_(type, buf, lenbuf, lenmes, nodeselect, nodefrom, sync)
     long *type;
     char *buf;
     long *lenbuf;
     long *lenmes;
     long *nodeselect;
     long *nodefrom;
     long *sync;
{
MPI_Status status;
int node = (int)*nodeselect;
int count = (int)*lenbuf;

     MPI_Recv(buf, count, MPI_CHAR, node, (int)*type, MPI_COMM_WORLD, &status);
     *nodefrom = (long)status.MPI_SOURCE;
     *lenmes   = (long)count;
}
 

void RingTest()
  /* Time passing a message round a ring */
{
  long me = NODEID;
  long type = 4;
  long left = (me + NNODES - 1) % NNODES;
  long right = (me + 1) % NNODES;
  char *buf, *buf2;
  unsigned char sum, sum2;
  long lenbuf, lenmes, nodefrom;
  double start, used, rate;
  long max_len;
  long i;
  long sync = 1;
  double lat=0;
  double lat2=0;
  double lat4=0;
  char *malloc();
  MPI_Status status;

  i = 0;
  lenbuf = sizeof(long);

  if (me == 0) {
    (void) printf("Ring test ... time network performance\n---------\n\n");
  }
      max_len = 512*1024;

  if ( (buf = malloc((unsigned) max_len)) == (char *) NULL)
    Error("failed to allocate buf",max_len);

  if (me == 0) {
    if ( (buf2 = malloc((unsigned) max_len)) == (char *) NULL)
      Error("failed to allocate buf2",max_len);

    for (i=0; i<max_len; i++)
      buf[i] = (char) (i%127);
  }

  type = 5;
  lenbuf = 1;
  while (lenbuf <= max_len) {
    int nloops = 500 + 1000/lenbuf;
    int loop = nloops;
    if (me == 0) {
      sum = CheckByte((unsigned char *) buf, lenbuf);
      (void) bzero(buf2, (int) lenbuf);
      start = MPI_Wtime();
      while (loop--) {
        MPI_Send(buf, lenbuf, MPI_CHAR, left, type, MPI_COMM_WORLD);
        MPI_Recv(buf2, lenbuf, MPI_CHAR, right, type, MPI_COMM_WORLD, &status);
      }
      used = MPI_Wtime() - start;
      sum2 = CheckByte((unsigned char *) buf2, lenbuf);
      if (used > 0)
        rate = 1.0e-6 * (double) (NNODES * lenbuf) / (double) used;
      else
        rate = 0.0;
      rate = rate * nloops;
      if(lenbuf==1) lat  = used/(NNODES*nloops);
      if(lenbuf==2) lat2 = used/(NNODES*nloops);
      if(lenbuf==4) lat4 = used/(NNODES*nloops);
      printf("len=%6ld bytes, nloop=%4ld, used=%8.4f s, rate=%8.4f Mb/s (0x%x, 0x%x)\n",
             lenbuf, nloops, used, rate, sum, sum2);
      (void) fflush(stdout);
    }
    else {
      while (loop--) {
        MPI_Recv(buf, lenbuf, MPI_CHAR, right, type, MPI_COMM_WORLD, &status);
        MPI_Send(buf, lenbuf, MPI_CHAR, left, type, MPI_COMM_WORLD);
      }
    }
    lenbuf *= 2;
  }

  if (me == 0){
    (void) free(buf2);
    printf("Latency (1/2 round-trip time for 1byte msg)=%8.1fus\n",1e6*lat);
    printf("Latency (1/2 round-trip time for 2byte msg)=%8.1fus\n",1e6*lat2);
    printf("Latency (1/2 round-trip time for 4byte msg)=%8.1fus\n",1e6*lat4);
  }

  (void) free(buf);
}


main(int argc, char** argv)
{
  MPI_Init(&argc, &argv);
  MPI_Errhandler_set(MPI_COMM_WORLD,MPI_ERRORS_ARE_FATAL); 
  MPI_Comm_rank(MPI_COMM_WORLD,&NODEID);
  MPI_Comm_size(MPI_COMM_WORLD,&NNODES);

  RingTest();

  MPI_Finalize();
}
  

