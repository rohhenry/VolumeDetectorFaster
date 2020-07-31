#Welfords Algo courtesy of Wikipedia       

# For a new value newValue, compute the new count, new mean, the new M2.
# mean accumulates the mean of the entire dataset
# M2 aggregates the squared distance from the mean
# count aggregates the number of samples seen so far

class Welfords:
    def __init__(self, count, mean, M2):
        self.count = count
        self.mean = mean
        self.M2 = M2
    
    def update(self, newValue):
        self.count += 1
        delta = newValue - self.mean
        self.mean += delta / self.count
        delta2 = newValue - self.mean
        self.M2 += delta * delta2
        return self.count, self.mean, self.M2

    # Retrieve the mean, variance and sample variance from an aggregate
    def finalize(self):
        (mean, variance, sampleVariance) = (self.mean, self.M2 / self.count, self.M2 / (self.count - 1))
        return (mean, variance, sampleVariance)