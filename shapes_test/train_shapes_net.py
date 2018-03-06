import caffe

solver = caffe.SGDSolver('shapes_net_solver.prototxt')
solver.solve()
