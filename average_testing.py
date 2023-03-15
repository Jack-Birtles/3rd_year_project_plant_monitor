temperature_examples = [15, 15.3, 15.7, 15.8, 16.0]
weights = [0.025, 0.1, 0.175, 0.2, 0.5]

mean = sum(temperature_examples) / len(temperature_examples)
weighted_avg = 0
for i,j in enumerate(temperature_examples):
    weighted_avg = weighted_avg + (j * weights[i])
    
print("mean: ", mean)
print("weighted average: ", weighted_avg)