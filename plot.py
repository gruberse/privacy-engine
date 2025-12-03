import matplotlib.pyplot as plt

fig, ax = plt.subplots()
x = [100, 200, 300, 400, 500]
fmt = 'o-'
ax.plot(x, [0.5, 0.63, 0.78, 0.9, 1.06], fmt, label='order')
ax.plot(x, [0.57, 0.66, 0.73, 0.8, 0.9], fmt, label='classification')
ax.plot(x, [1.2, 1.84, 2.48, 3.1, 3.79], fmt, label='buckets')
ax.plot(x, [0.71, 0.98, 1.22, 1.43, 1.68], fmt, label='quantiles')
ax.plot(x, [0.49, 0.63, 0.77, 0.92, 1.05], fmt, label='top')
ax.set_xlabel('population size')
ax.set_ylabel('time (s)')
ax.set(xlim=(100, 500), xticks=[100, 200, 300, 400, 500])
plt.legend(title='methods')
plt.title('one iteration with matrix of size 100x100')
plt.show()

fig, ax = plt.subplots()
x = [20, 40, 60, 80, 100]
fmt = 'o-'
ax.plot(x, [0.99, 1.01, 1.04, 1.04, 1.06], fmt, label='order')
ax.plot(x, [0.82, 0.83, 0.87, 0.87, 0.90], fmt, label='classification')
ax.plot(x, [3.69, 3.73, 3.73, 3.77, 3.79], fmt, label='buckets')
ax.plot(x, [1.57, 1.61, 1.63, 1.67, 1.68], fmt, label='quantiles')
ax.plot(x, [0.98, 1.03, 1.03, 1.04, 1.05], fmt, label='top')
ax.set_xlabel('matrix size')
ax.set_ylabel('time (s)')
ax.set(xlim=(20, 100), xticks=[20, 40, 60, 80, 100])
plt.legend(title='methods')
plt.title('one iteration with population of size 500')
plt.show()
