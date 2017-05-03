procedure gen_colormap ( cmap[*][*]:float )
begin
        ; This procedure explicitly sets the red, green, and blue
        ; intensities for each element in a colormap array.
        ; It is based on HSV where sat and val equal 100%
        ; AND internet web-browser accepted color values
        ; of 0,20,60,80,100% of the R,G,B components.
 
        ; Entry 0 is the background color
        cmap(  0, :) = (/1.0, 1.0, 1.0/)
        ; Entry 1 is the foreground color and map objects
        cmap(  1, :) = (/0.0, 0.0, 0.0/)
 
        cmap(  2, :) = (/1.0, 0.0, 0.8/)
        cmap(  3, :) = (/1.0, 0.0, 1.0/)
        cmap(  4, :) = (/0.8, 0.0, 1.0/)
        cmap(  5, :) = (/0.6, 0.0, 1.0/)
        cmap(  6, :) = (/0.4, 0.0, 1.0/)
        cmap(  7, :) = (/0.2, 0.0, 1.0/)
        cmap(  8, :) = (/0.0, 0.0, 1.0/)
        cmap(  9, :) = (/0.0, 0.2, 1.0/)
        cmap( 10, :) = (/0.0, 0.4, 1.0/)
        cmap( 11, :) = (/0.0, 0.6, 1.0/)
        cmap( 12, :) = (/0.0, 0.8, 1.0/)
        cmap( 13, :) = (/0.0, 1.0, 1.0/)
        cmap( 14, :) = (/0.0, 1.0, 0.8/)
        cmap( 15, :) = (/0.0, 1.0, 0.6/)
        cmap( 16, :) = (/0.0, 1.0, 0.4/)
        cmap( 17, :) = (/0.0, 1.0, 0.2/)
        cmap( 18, :) = (/0.0, 1.0, 0.0/)
        cmap( 19, :) = (/0.2, 1.0, 0.0/)
        cmap( 20, :) = (/0.4, 1.0, 0.0/)
        cmap( 21, :) = (/0.6, 1.0, 0.0/)
        cmap( 22, :) = (/0.8, 1.0, 0.0/)
        cmap( 23, :) = (/1.0, 1.0, 0.0/)
        cmap( 24, :) = (/1.0, 0.8, 0.0/)
        cmap( 25, :) = (/1.0, 0.6, 0.0/)
        cmap( 26, :) = (/1.0, 0.4, 0.0/)
        cmap( 27, :) = (/1.0, 0.2, 0.0/)
        cmap( 28, :) = (/1.0, 0.0, 0.0/)
        cmap( 29, :) = (/1.0, 0.0, 0.2/)
        cmap( 30, :) = (/1.0, 0.0, 0.4/)
        cmap( 31, :) = (/1.0, 0.0, 0.6/)
        ; Entry 32+ is a gray color scale
        cmap( 32, :) = (/0.8, 0.8, 0.8/)
        cmap( 33, :) = (/0.7, 0.7, 0.7/)
        cmap( 34, :) = (/0.6, 0.6, 0.6/)
        cmap( 35, :) = (/0.5, 0.5, 0.5/)
        cmap( 36, :) = (/0.4, 0.4, 0.4/)
end
