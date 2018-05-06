from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from deep_introspection import synthesis

from apps.uploadModel.models import TestModel
from apps.uploadImage.models import TestImage
from apps.synthesis.models import FeatureImage
from apps.features.views import read_clusters

@csrf_exempt
def index (request, model, image, feature):
    if request.method == 'GET':
        images = map(lambda x: x.feature_image, FeatureSet.objects.filter(model__id=model,image__id=image, feature=feature))
        return HttpResponse("{\"images\": " + images +"}")
    else:
        return HttpResponse("{message: \"Invalid method.\"}", status=405)


@csrf_exempt
def synthesise(request, model, image, feature):
    if request.method == 'POST':
        features_path = 'features/model_'+ str(model) + '_image_' + str(image) + '.dat'

        body = json.loads(request.body.decode("utf-8"))
        feature = body['feature']
        clusters = read_clusters(features_path)

        cluster = np.array(clusters[feature])


        img_path = TestImage.objects.filter(id=image).first().image
        test_model = TestModel.objects.filter(id=model).first()

        architecture = str(test_model.architecture)
        weights = str(test_model.weights)
        labels = str(test_model.labels)

        if architecture.split(".")[-1].lower() == "meta":
            net = network.TensorFlowNet(architecture, './models/'+ str(test_model.user) +'_' + test_model.name + '/')
            img = imread(img_path, mode='RGB')
            img = imresize(img, (224, 224))

        else:
            net = network.CaffeNet(architecture, weights)
            img, offset, resFac, newSize = utils.imgPreprocess(img_path=img_path)
            net.set_new_size(newSize)

        xmax, ymax, xmin, ymin = np.max(cluster[:,0]), np.max(cluster[:,1]), np.min(cluster[:,0]), np.min(cluster[:,1])

        feature_img, _ = synthesis.synthesise_boundary(net, img, xmax, ymax, xmin, ymin)

        num = FeatureSet.objects.filter(model__id=model,image__id=image).count()

        # save synthesised image
        feature_img = Image.fromarray(np.uint8(feature_img))
        feature_path = 'synthesised_images/model_'+ str(model) + '_image_' + str(image) + '_' + str(feature) + '_' + str(num) + '.jpg'
        feature_img.save(feature_path)

        featureImage = FeatureImage(model__id = model, image__id=image, feature=feature, feature_image=feature_path)
        featureImage.save()
        return HttpResponse("{\"image\": " + modification_path +"}")
    else:
        return HttpResponse("{message: \"Invalid method.\"}", status=405)
