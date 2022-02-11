import random
import torch
from tqdm import tqdm


def train(input, counts, decoder, decoder_optimizer, criterion_class, criterion_count, dataset, acceptance_level=0.5, teacher_forcing_ratio=1):
    decoder_optimizer.zero_grad()

    target_length = input.shape[0]

    loss_class = 0
    loss_count = 0

    use_teacher_forcing = True if random.random() < teacher_forcing_ratio else False

    # merging first chord and number of it's ocurences
    decoder_input = torch.cat((input[0], counts[0].view(1, -1)), dim=1)
    decoder_hidden = (decoder.initHidden(), decoder.initHidden())  # LSTM
    decoder_hidden = decoder.initHidden()  # GRU

    if use_teacher_forcing:
        for i in range(1, target_length):
            decoder_output_class, decoder_output_count, decoder_hidden = decoder(
                decoder_input, decoder_hidden)

            # Based on i-1 chord does model predicted ith chord?
            loss_class += criterion_class(decoder_output_class, input[i])
            #print(decoder_output_count, counts[i])
            loss_count += criterion_count(decoder_output_count, counts[i])

            # i ths chord is input to the next iteration
            decoder_input = torch.cat((input[i], counts[i].view(1, -1)), dim=1)
    else:
        for i in range(1, target_length):
            print(decoder_input)
            decoder_output_class, decoder_output_count, decoder_hidden = decoder(
                decoder_input, decoder_hidden)

            # Based on i-1 chord does model predicted ith chord?
            loss_class += criterion_class(decoder_output_class, input[i])
            #print(decoder_output_count, counts[i])
            loss_count += criterion_count(decoder_output_count, counts[i])

            chords_predicted = (decoder_output_class > acceptance_level).type(
                dtype=torch.float32).detach()
            counts_predicted = torch.exp(decoder_output_count.detach())
            # ! I shouldn't be givin count predicted here!
            decoder_input = torch.cat((chords_predicted, counts[i]), dim=1)

        # THERE also is a problem with this loss_count, since it sometimes may be very big. And network became unstable in a moment!
        # Since this is propated through entire network entire network became a trash in a moment

        # This is problably not the best idea, let it go through whole target. Not to stop too early
        # if decoder_input[0, dataset.word2num[END_TOKEN]] == 1:
        #    break

    loss_class.backward()
    # loss_count.backward()  # Now I cen delete the graph
    #print(loss_class, loss_count)
    # loss = loss_class + loss_count #! WE CAN'T SUM UM THESE LOSSES Loss_count basically can take as big negative numbers as we wish!!!!!
    # loss_class.backward(retain_graph=True) #During first iteration I retain computational graph to be able to do backward once more
    # loss_count.backward() #Now I cen delete the graph
    if torch.isnan(loss_class):
        print("NAN!! CLASS")
    if torch.isnan(loss_count):
        print("NAN!! COUNT")
    decoder_optimizer.step()

    return loss_class.item() / target_length, loss_count.item() / target_length


def train_epoch(dataloader, decoder, decoder_optimizer, criterion_class, criterion_count, dataset, device):
    loop = tqdm(dataloader, leave=True)
    losses_class = []
    losses_count = []
    for batch_idx, (input, count) in enumerate(loop):
        input, count = input.to(device), count.to(device)
        # print(input.shape)
        loss_class, loss_count = train(
            input[0], count[0], decoder, decoder_optimizer, criterion_class, criterion_count, dataset)
        losses_class.append(loss_class)
        losses_count.append(loss_count)
        # update tqdm loop
        loop.set_postfix(loss_class=loss_class, loss_count=loss_count)

    return sum(losses_class) / len(losses_class), sum(losses_count) / len(losses_count)
