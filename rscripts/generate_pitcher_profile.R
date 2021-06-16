
library(DBI)
conn <- dbConnect(RPostgres::Postgres(),
    dbname = 'mlb_bak',
    host = 'localhost',
    port = '5432',
    user = 'ilara',
    password = 'temp_passwd'
)
pitcher_ids = dbGetQuery(conn, "select playerid from players where pos='P'")

library(glue)
generate_query <- function(x) {
    pitcher_profile = "
        select type, count(*)
        from
            (
                select atbatid
                from atbats
                where pitcherid = {x}
            ) a
        inner join 
            (
                select * from pitchseq 
                where type is not null
                and type <> 'Automatic Ball'
                and type <> 'Pitchout'
            ) b
        on a.atbatid = b.atbatid
        group by type
        order by type
    "
    return(glue(pitcher_profile))
}

df = data.frame()
types = dbGetQuery(conn,
    "select type
     from pitchseq 
     group by type 
     having type is not null
     and type<>'Pitchout'
     and type<>'Automatic Ball'"
)
for (type in types[,1]) {
    df[type] = numeric()
}
for (playerid in pitcher_ids[,1]) {
    table = dbGetQuery(conn, generate_query(playerid))
    table = table[complete.cases(table),]
    tot = sum(table[,2])
    if (tot >= 500) {
        table[,2] = round(table[,2]/tot, digits=6)
        idx = nrow(df) + 1
        df[idx,] = 0
        df[idx,'id'] = playerid
        for (i in 1:nrow(table)) {
            df[idx, table[i,1]] = table[i,2]
        }
    }
}
save(df, file='pitcher_profile.Rda')
