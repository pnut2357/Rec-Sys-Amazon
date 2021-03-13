import itertools

from surprise import accuracy
from collections import defaultdict

class RecommenderMetrics:

    def MAE(predictions):
        return accuracy.mae(predictions, verbose=False)

    def RMSE(predictions):
        return accuracy.rmse(predictions, verbose=False)

    def GetTopN(predictions, n=10, minimumRating=4.0):
        topN = defaultdict(list)


        for userID, itemID, rating, est, _ in predictions:
#            pred = int(pred)
            if (est >= minimumRating):
                topN[userID].append((itemID, est))

        for userID, itemRating in topN.items():
            #temp = []
            #temp.append(itemRating)
            itemRating.sort(key=lambda x: x[1], reverse=True)
            topN[userID] = itemRating[:n]

        return topN

    def HitRate(topNPredicted, leftOutPredictions):
        hits = 0
        total = 0

        # For each left-out rating
        for leftOut in leftOutPredictions:
            userID = leftOut[0]
            leftOutItemID = leftOut[1]
            # Is it in the predicted top 10 for this user?
            hit = False
            for id_pred in topNPredicted[userID]:
                itemID, predictedRating = id_pred
                if (leftOutItemID == itemID):
                    hit = True
                    break
            if (hit) :
                hits += 1

            total += 1

        # Compute overall precision
        return hits/total

    def CumulativeHitRate(topNPredicted, leftOutPredictions, ratingCutoff=0):
        hits = 0
        total = 0

        # For each left-out rating
        for userID, leftOutItemID, rating, est, _ in leftOutPredictions:
            # Only look at ability to recommend things the users actually liked...
            if (rating >= ratingCutoff):
                # Is it in the predicted top 10 for this user?
                hit = False
                for id_pred in topNPredicted[userID]:
                    itemID, predictedRating = id_pred
                    if (leftOutItemID == itemID):
                        hit = True
                        break
                if (hit) :
                    hits += 1

                total += 1

        # Compute overall precision
        return hits/total

    def RatingHitRate(topNPredicted, leftOutPredictions):
        hits = defaultdict(float)
        total = defaultdict(float)

        # For each left-out rating
        for userID, leftOutItemID, rating, est, _ in leftOutPredictions:
            # Is it in the predicted top N for this user?
            hit = False
            for id_pred in topNPredicted[userID]:
                itemID, predictedRating = id_pred
                if (leftOutItemID == itemID):
                    hit = True
                    break
            if (hit) :
                hits[rating] += 1

            total[rating] += 1

        # Compute overall precision
        for rate in sorted(hits.keys()):
            print(rate, hits[rate] / total[rate])

    def AverageReciprocalHitRank(topNPredicted, leftOutPredictions):
        summation = 0
        total = 0
        # For each left-out rating
        for userID, leftOutItemID, rating, est, _ in leftOutPredictions:
            # Is it in the predicted top N for this user?
            hitRank = 0
            rank = 0
            for id_pred in topNPredicted[userID]:
                itemID, predictedRating = id_pred
                rank = rank + 1
                if (leftOutItemID == itemID):
                    hitRank = rank
                    break
            if (hitRank > 0) :
                summation += 1.0 / hitRank

            total += 1

        return summation / total

    # What percentage of users have at least one "good" recommendation
    def UserCoverage(topNPredicted, numUsers, ratingThreshold=0):
        hits = 0
        for userID in topNPredicted.keys():
            hit = False
            for id_pred in topNPredicted[userID]:
                movieID, predictedRating = id_pred
                if (predictedRating >= ratingThreshold):
                    hit = True
                    break
            if (hit):
                hits += 1

        return hits / numUsers

    def Diversity(topNPredicted, simsAlgo):
        n = 0
        total = 0
        simsMatrix = simsAlgo.compute_similarities()
        for userID in topNPredicted.keys():
            pairs = itertools.combinations(topNPredicted[userID], 2)
            for pair in pairs:
                movie1 = pair[0][0]
                movie2 = pair[1][0]
                innerID1 = simsAlgo.trainset.to_inner_iid(str(movie1))
                innerID2 = simsAlgo.trainset.to_inner_iid(str(movie2))
                similarity = simsMatrix[innerID1][innerID2]
                total += similarity
                n += 1

        S = total / n
        return (1-S)
    
    def getPopularityRanks(data):
        ratings = defaultdict(int)
        rankings = defaultdict(int)
        # num of ratings per item
        item_num = data.groupby(by='asin')['overall'].count().sort_values(ascending=False)
        rank = 1
        for itemID, ratingCount in item_num.iteritems():
            rankings[itemID] = rank
            rank += 1
        return rankings
    
    def Novelty(topNPredicted, rankings):
        n = 0
        total = 0
        for userID in topNPredicted.keys():
            for rating in topNPredicted[userID]:
                movieID = rating[0]
                rank = rankings[movieID]
                total += rank
                n += 1
        return total / n
