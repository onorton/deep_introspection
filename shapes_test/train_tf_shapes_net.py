import numpy as np
import tensorflow as tf

def cnn_model_fn(features, labels, mode):
  """Model function for CNN."""
  # Input Layer
  input_layer = tf.reshape(features["x"], [-1, 112, 112, 1])
  # Convolutional Layer #1
  conv1 = tf.layers.conv2d(
      inputs=input_layer,
      filters=32,
      kernel_size=[5, 5],
      padding="same",
      activation=tf.nn.relu)
  # Pooling Layer #1
  pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)

  # Convolutional Layer #2 and Pooling Layer #2
  conv2 = tf.layers.conv2d(
        inputs=pool1,
        filters=64,
        kernel_size=[7, 7],
        padding="same",
        activation=tf.nn.relu)
  pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[2, 2], strides=2)


  conv3 = tf.layers.conv2d(
        inputs=pool2,
        filters=64,
        kernel_size=[7, 7],
        padding="same",
        activation=tf.nn.relu)
  pool3 = tf.layers.max_pooling2d(inputs=conv3, pool_size=[2, 2], strides=2)


  # Dense Layer
  pool3_flat = tf.reshape(pool3, [-1, 14 * 14 * 64])
  dense_1 = tf.layers.dense(inputs=pool3_flat, units=4096, activation=tf.nn.relu)
  dropout_1 = tf.layers.dropout(inputs=dense_1, rate=0.5, training=mode == tf.estimator.ModeKeys.TRAIN)
  # Logits Layer
  logits = tf.layers.dense(inputs=dropout_1, units=2)

  predictions = {
      # Generate predictions (for PREDICT and EVAL mode)
      "classes": tf.argmax(input=logits, axis=1),
      # Add `softmax_tensor` to the graph. It is used for PREDICT and by the
      # `logging_hook`.
      "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
  }

  if mode == tf.estimator.ModeKeys.PREDICT:
    return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

  # Calculate Loss (for both TRAIN and EVAL modes)
  loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

  # Configure the Training Op (for TRAIN mode)
  if mode == tf.estimator.ModeKeys.TRAIN:
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.00001)
    train_op = optimizer.minimize(
        loss=loss,
        global_step=tf.train.get_global_step())
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

  # Add evaluation metrics (for EVAL mode)
  eval_metric_ops = {
      "accuracy": tf.metrics.accuracy(
          labels=labels, predictions=predictions["classes"])}
  return tf.estimator.EstimatorSpec(
      mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)

tf.logging.set_verbosity(tf.logging.INFO)

# Our application logic will be added here

  # Load training and eval data
train_data = np.load('train_images.npy')
train_labels = np.asarray(np.load('train_labels.npy'), dtype=np.int32)
eval_data =np.load('test_images.npy') # Returns np.array
eval_labels = np.asarray(np.load('test_labels.npy'), dtype=np.int32)
shape_classifier = tf.estimator.Estimator(
  model_fn=cnn_model_fn, model_dir="/tmp/shape_model")
tensors_to_log = {"probabilities": "softmax_tensor"}
logging_hook = tf.train.LoggingTensorHook(
  tensors=tensors_to_log, every_n_iter=50)
train_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": train_data},
    y=train_labels,
    batch_size=128,
    num_epochs=None,
    shuffle=True)
shape_classifier.train(
    input_fn=train_input_fn,
    steps=4000,
    hooks=[logging_hook])
val_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": eval_data},
    y=eval_labels,
    num_epochs=1,
    shuffle=False)
eval_results = shape_classifier.evaluate(input_fn=eval_input_fn)
print(eval_results)
