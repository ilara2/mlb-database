
options(width = 160)
load('pitcher_profile.Rda')

k = kmeans(df[,1:13], 5, iter.max = 100, nstart = 100)
pdf
for (j in 1:5) {
    one = data.frame()
    for (i in 1:20){
        tmp = kmeans(df[c(order(k$cluster[k$cluster==j])),], i, nstart = 100, iter.max = 100)
        idx = nrow(one)+1
        one[idx,] = 0
        one[idx, 1] = i
        one[idx, 2] = tmp$betweenss / tmp$totss
        one[idx, 3] = max(tmp$withinss)
    }

    pdf(glue("{j}.pdf"))
    plot(one[,1], one[,3], xlab="Number of Centers", ylab="Total within-cluster sum of squares")
    dev.off()
}
