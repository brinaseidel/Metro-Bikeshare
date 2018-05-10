library("ggmap")
stations <- read.csv("/Users/brinaseidel/Documents/School/GA Data Science/Final Project/Output Data/Bikeshare Stations.csv")
stations = transform(stations, min_dist = pmin(red_dist, blue_dist, green_dist, yellow_dist, orange_dist, silver_dist))
stations$close = "More than 0.5mi from Metro"
stations$close[stations$min_dist <= .5] = "Within 0.5mi from Metro"
table(stations$close)
stations$close = factor(stations$close)

# Set map dimensions
bbox <- make_bbox(lon = stations$lon, lat = stations$lat, f = .15)
bbox
# Get DC map
dc_map <- get_map(location = bbox, maptype = "terrain", source = "google")
ggmap(dc_map) + geom_point(data = stations, mapping = aes(x = lon, y = lat, color=close), size=1.1) +
  scale_color_manual(values=c( "#777777", "#1c943a")) +
  theme(axis.title.x=element_blank(), axis.title.y=element_blank(),
        axis.text.x=element_blank(), axis.text.y=element_blank(),
        axis.ticks.x=element_blank(), axis.ticks.y=element_blank(), 
        legend.title=element_blank(), legend.position="bottom")
