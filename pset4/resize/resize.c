/**
 * Copies a BMP piece by piece, just because.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "bmp.h"

void enlarge(uint8_t * row, int new_width, int old_width, FILE * outptr, int padding);

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: ./resize resize_factor infile outfile\n");
        return 1;
    }
    //argv[1]: floating point scalar
    //argv[2]: input file
    //argv[3]: output file

    // remember filenames
    float scale = atof(argv[1]); // lies in (0.0, 100.0]
    char *infile = argv[2]; //sizeof(scale * infile) <= (2^32) - 1
    char *outfile = argv[3];

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    if(scale < 0.0 || scale > 100.0)
    {
        fprintf(stderr, "Resize_factor is out of range.\n");
        fprintf(stderr, "Usage: 0.0 <= resize factor <= 100.0");
        return 1;
    }

    if((scale - 1.0000) < 0.00001)
    {
        int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4; //should be valid even after scaling
        // write outfile's BITMAPFILEHEADER
        fwrite(&bf, sizeof(BITMAPFILEHEADER), 1, outptr);

        // write outfile's BITMAPINFOHEADER
        fwrite(&bi, sizeof(BITMAPINFOHEADER), 1, outptr);
        for (int i = 0, biHeight = abs(bi.biHeight); i < biHeight; i++)
        {
            // iterate over pixels in scanline
            for (int j = 0; j < bi.biWidth; j++)
            {
                // temporary storage
                RGBTRIPLE triple;

                // read RGB triple from infile
                fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

                // write RGB triple to outfile
                fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);
            }

            // skip over padding, if any
            fseek(inptr, padding, SEEK_CUR);

            // then add it back (to demonstrate how)
            for (int k = 0; k < padding; k++)
            {
                fputc(0x00, outptr);
            }
        }
        return 0;
    }

    //grab original dimensions
    int orig_width = bi.biWidth;
    int orig_height = bi.biHeight;


    //Modify BITMAPINFOHEADER
    bi.biWidth = (LONG) ((float) bi.biWidth * scale); //should go to whole number since we're type casting
    bi.biHeight = (LONG) ((float) bi.biHeight * scale);

    //need padding to determine total image size
    int padding =  (4 - ((bi.biWidth * sizeof(RGBTRIPLE)) % 4)) % 4; // number of bytes to pad

    // bi.biSizeImage = (DWORD) ((bi.biWidth + padding) * abs(bi.biHeight) * 3);
    bi.biSizeImage = (DWORD) (((bi.biWidth * sizeof(RGBTRIPLE)) + padding) * abs(bi.biHeight));

    //Modify BITMAPFILEHEADER
    //14 bytes for bitmapfileheader and 40 bytes for bitmapinfoheader and biSizeImage
    bf.bfSize = (DWORD) (14 + 40 + bi.biSizeImage);

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi, sizeof(BITMAPINFOHEADER), 1, outptr);

    int total_height = 0; //keeps track of height of new .bmp image

    padding =  (4 - ((orig_width * sizeof(RGBTRIPLE)) % 4)) % 4; // number of bytes to pad

    // int count = 0;
    uint8_t *row = malloc(orig_width * sizeof(RGBTRIPLE));
    uint8_t *garbage = malloc(padding * sizeof(RGBTRIPLE));
    float row_count = 0.0; //COMMENT OUT
    for (int i = 0; i < abs(orig_height); i++)
    {
        //grab row of existing bmp first
        for (int j = 0; j < (orig_width * sizeof(RGBTRIPLE) + padding); j++) //now j sweeps over bytes, not pixels
        {

            if(orig_width % 4 != 0)
            {
                if(j < (orig_width * sizeof(RGBTRIPLE)))
                {
                    // fread(row + (sizeof(RGBTRIPLE) * j), sizeof(RGBTRIPLE), 1, inptr);
                    fread(row + j, sizeof(uint8_t), 1, inptr);
                    // printf("i: %i, j: %i, orig_width mod 4 IS zero\n", i, j);
                }
                else
                {
                    // fread(garbage, sizeof(RGBTRIPLE), 1, inptr); //padding * 3 for three bytes
                    fread(garbage, sizeof(uint8_t), 1, inptr);
                    // printf("i: %i, j: %i, not going to record garbage\n", i, j);
                }
            }
            else
            {
                // fread(row + (sizeof(RGBTRIPLE) * j), sizeof(RGBTRIPLE), 1, inptr);
                fread(row + j, sizeof(uint8_t), 1, inptr);
                // printf("i: %i, j: %i, orig_width mod 4 IS zero\n", i, j);
            }
        }

        while((total_height < abs(bi.biHeight)) && (row_count < (float) ((float) bi.biHeight/(float) orig_height) * (float) (i + 1)))
        {
            //now that we have all original pixels in the ith row, scale and output:
            enlarge(row, bi.biWidth, orig_width, outptr, padding);

            total_height++;
            row_count++;
        }
    }
    //free row
    free(row);
    free(garbage);

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}

void enlarge(uint8_t * row, int new_width, int old_width, FILE * outptr, int padding)
{


    int total_width = 0;
    float pixel_count = 0.0;
    // printf("new_width: %i, old_width: %i\n", new_width, old_width);
    for(int i = 0; i < old_width; i++)
    {

        while((total_width < new_width) && (pixel_count < (float) ((float) new_width/(float) old_width) * (float) (i + 1)))
        {

            fwrite(row + (sizeof(RGBTRIPLE) * i), sizeof(uint8_t), 1, outptr);
            fwrite(row + 1 + (sizeof(RGBTRIPLE) * i), sizeof(uint8_t), 1, outptr);
            fwrite(row + 2 + (sizeof(RGBTRIPLE) * i), sizeof(uint8_t), 1, outptr);
            // printf("To file: %x, %x, %x\n", *(row + (sizeof(RGBTRIPLE) * i)),
            //     *(row + 1 + (sizeof(RGBTRIPLE) * i)), *(row + 2 + (sizeof(RGBTRIPLE) * i)));
            // printf("p_c: %f, limit: %f\n", pixel_count, (float) ((float) new_width/(float) old_width) * (float) (i + 1));
            pixel_count++;
            total_width++;
        }
    }
    padding = (4 - (new_width * sizeof(RGBTRIPLE)) % 4) % 4;

    // add back in padding
    for (int k = 0; k < padding; k++)
    {
        fputc(0x00, outptr);
    }
}