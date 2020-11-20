###############################################################################
# Sample code to generate maps for the statistical atlas
###############################################################################

# Original Atlas Map Code By A. Loy
# Modified By J. Hobbs

### Preliminaries -------------------------------------------------------------

library(ggplot2)   # for plotting
library(reshape2)  # for data munging
library(plyr)      # for data munging/aggregating
library(sp)        # for spatial polygons (needed for huc6 labels)
library(gridExtra) # some extra grid graphics goodies

# Reading in weather data
weather <- read.csv("WeatherHUC6.csv")

### Mapping tools and setup ---------------------------------------------------
# load the state polygons
states <- read.csv("state_polygons.csv")

# load the HUC6 polygons
huc <- read.csv("huc6_polygons.csv")
#huc <- ddply(huc, .(HUC6), transform, huc6.number = HUC6, order = seq_len(length(HUC6)))
#huc <- subset(huc, select = -HUC6)
#levels(huc$ACC_NAME) <- levels(cscap$huc6_name)

# defining a the centroids of the watersheds
huc6.centroids <- ddply(huc, c("huc6_name"), .fun = function(x){
  RVAL <- Polygon(x[,c("longitude", "latitude")])@labpt
  names(RVAL) <- c("longitude", "latitude")
	return(RVAL)
})

# adding the watershed names to huc6.centroids for mapping
huc6.centroids$map.labels <- c(
	"Big\nBlue", 
	"Big\nSioux", 
	"Des\nMoines",
	"Elkhorn",
	"Iowa", 
	"Kaskaskia",
	"Loup",
	"Lower\nIllinois",
	"Lower\nPlatte",
	"Middle Platte",
	"Minnesota",
	"Missouri\nLittle\nSioux",
	"Missouri\n Nishnabotna",
	"Patoka\nWhite",
	"Rock",
	"Southeastern\nLake\nMichigan",
	"Upper\nIllinois",
	"Black Root",
	"Maquoketa\nPlum",
	"Skunk\nWapsipinicon",
	"Wabash",
	"Western\nLake Erie")

# manually adjusting some plotting locations
huc6.centroids[c(2, 3, 6, 9, 10, 11, 12, 15, 17, 18, 19, 20, 21),"latitude"] <- c(43.8, 42.7, 38.6, 41.1, 40.75, 44.5, 42.25, 42.35, 41.35, 44.18, 42.74, 40.88, 40)
huc6.centroids[c(2, 3, 4, 5, 6, 9, 12, 13, 16, 17, 20, 21),"longitude"] <- c(-96.5, -94.42, -97.4, -92.65, -89.55, -96.6, -95.8, -95.6, -85.1, -88, -91.4, -87.45)


# defining additional theme elements for maps
map_themes <- theme(
  axis.text.x = element_blank(), 
  axis.text.y = element_blank(),
  axis.title.x = element_blank(), 
  axis.title.y = element_blank(),
  axis.ticks = element_line(colour=rgb(0,0,0,alpha=0)),
  panel.background =  element_blank(),
  panel.grid.major =  element_blank(),
  panel.grid.minor =  element_blank(),
  plot.margin = unit(c(0,0,0,0), "lines")
  )
  
# function to format discretized legend
format.legend.labels <- function(labs) {
  RVAL <- sub("\\(", "\\1", labs)
  RVAL <- sub("\\]", "\\1", RVAL)
  RVAL <- sub(",", " - ", RVAL)
  
  return(RVAL)
}

# function defining breaks for the colourbar legend
breaks.legend <- function(x, len) {
#   RVAL <- seq(floor(min(x)), ceiling(max(x)), length.out = len)
  RVAL <- seq(min(x), max(x), length.out = len)
  return(RVAL)
}

# function to adjust rounding on the legends
label.legend <- function(x, len, digits=0) {
  RVAL <- seq(min(x), max(x), length.out = len)
  return(round(RVAL, digits))
}

# East to west order
geographic.order <- c("Western Lake Erie", "Southeastern Lake Michigan", "Patoka-White", "Wabash", "Upper Illinois", "Kaskaskia", "Rock", "Lower Illinois", "Maquoketa Plum", "Skunk Wapsipinicon", "Black Root", "Iowa", "Des Moines", "Minnesota", "Missouri-Nishnabotna", "Missouri-Little Sioux", "Big Sioux", "Lower Platte", "Big Blue", "Elkhorn", "Middle Platte", "Loup")

# West to east order
geographic.order <- rev(geographic.order)


### Example Map 1 -------------------------------------------------------------

wxsb = weather[,c("huc6_id","SeasPrcp07")]

# merging the weather data with the HUC6 plotting information
prcp_huc6 <- merge(x = huc, y = wxsb)

# reordering after the merge -- this makes sure the plotting order is 
# preserved for the polygon geometry
prcp_huc6 <- prcp_huc6[order(prcp_huc6$huc6_name, prcp_huc6$poly_id, prcp_huc6$vert_ord),]
# Multiply percentile rank by 100
prcp_huc6$SeasPrcp07 = prcp_huc6$SeasPrcp07 * 100

# creating a map for seasonal precip
g1 = ggplot(states, aes(longitude, latitude, group = poly_id)) +
  geom_polygon(data = states, colour = "gray30", fill = NA, size = 0.5) +
  geom_polygon(aes(x = longitude, y = latitude, fill = SeasPrcp07, group = poly_id), 
               data = prcp_huc6, inherit.aes = FALSE, 
               colour = "black", alpha = .9, size = 0.2) + 
  scale_fill_gradient("Pct Rank",
                      low = "#99CCFF", high = "#000099") + 
  geom_text(aes(label = map.labels, x = longitude, y = latitude, group = huc6_name), 
            data = huc6.centroids, size = 2, lineheight = .7, 
            colour = "black") + coord_fixed(ratio=1) + 
  map_themes

pdf("SeasPrcpMap.pdf",width=8,height=6)
print(g1)
dev.off()
