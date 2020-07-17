import torch
import torch.nn as nn
import torchvision.models as models
from efficientnet import EfficientNet

class Classifier(nn.Module):
    def __init__(self, num_classes):
        super(Classifier, self).__init__()
        self.model = models.resnet50(pretrained=True)
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)

    def forward(self, x):
        x = self.model(x)
        for name, param in self.model.named_parameters():
            if 'fc.weight' in name or 'fc.bias' in name:
                param.requires_grad = True
            else:
                param.requires_grad = False

        return x


class efft(nn.Module):
    def __init__(self, num_classes, weights=None):
        super(efft, self).__init__()
        self.EfficientNet = EfficientNet.from_pretrained('efficientnet-b{}'.format(weights), num_classes)

    def forward(self, x):
        x = self.EfficientNet(x)

        return x