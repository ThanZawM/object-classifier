import torch
import tqdm
import time
import copy
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter('logs')

def train_model(model, loader, size, criterion, optimizer, scheduler, num_epochs, device):
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    
    for epoch in range(num_epochs):
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()
            mloss = torch.zeros(4, device=device)  # mean losses
            running_loss = 0.0
            running_corrects = 0.0

            pbar= tqdm.tqdm(enumerate(loader[phase]), total=len(loader[phase]))
            for i, (inputs, labels) in pbar:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, pred = torch.max(outputs, 1)

                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(pred == labels.data)

                mloss = (mloss * i + running_loss) / (i + 1)  # update mean losses
                mem = '%.3gG' % (torch.cuda.memory_cached() / 1E9 if torch.cuda.is_available() else 0)  # (GB)
                s = ('%10s' * 2 + '%10.4g' * 6) % (
                    'Epoch: %g/%g' % (epoch+1, num_epochs), mem, *mloss, labels.shape[0], inputs.shape[-1])
                pbar.set_description(s)

            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / size[phase]
            epoch_acc = running_corrects / size[phase]
            
                
            if phase == 'train':
                writer.add_scalar('loss', epoch_loss, epoch+1)
                writer.add_scalar('acc', epoch_acc, epoch+1)
            else:
                writer.add_scalar('val loss', epoch_loss, epoch+1)
                writer.add_scalar('val acc', epoch_acc, epoch+1)

            print('{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc))

            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

        print()

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
            time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))
        # load best model weights
    model.load_state_dict(best_model_wts)
    checkpoint = {
                'state_dict' : model.state_dict(),
                'optimizer' : optimizer.state_dict()
            }
    torch.save(checkpoint, 'weights/best_model.pth')
    return model