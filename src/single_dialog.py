from __future__ import absolute_import
from __future__ import print_function

from data_utils import load_dialog_task, vectorize_data, load_candidates, load_test_candidates, vectorize_candidates, vectorize_data_with_surface_form, vectorize_candidates_sparse, tokenize, restaurant_reco_evluation, load_dialog_test_data
from sklearn import metrics
from memn2n import MemN2NDialog
from itertools import chain
from six.moves import range, reduce
from operator import itemgetter
import sys
import tensorflow as tf
import numpy as np
import os
import pdb
import json

tf.flags.DEFINE_float("learning_rate", 0.01,
                      "Learning rate for Adam Optimizer.")
tf.flags.DEFINE_float("epsilon", 1e-8, "Epsilon value for Adam Optimizer.")
tf.flags.DEFINE_float("max_grad_norm", 40.0, "Clip gradients to this norm.")
tf.flags.DEFINE_integer("evaluation_interval", 10,
                        "Evaluate and print results every x epochs")
tf.flags.DEFINE_integer("batch_size", 32, "Batch size for training.")
tf.flags.DEFINE_integer("hops", 1, "Number of hops in the Memory Network.")
tf.flags.DEFINE_integer("epochs", 200, "Number of epochs to train for.")
tf.flags.DEFINE_integer("embedding_size", 32,
                        "Embedding size for embedding matrices.")
tf.flags.DEFINE_integer("memory_size", 50, "Maximum size of memory.")
tf.flags.DEFINE_integer("task_id", 1, "bAbI task id, 1 <= id <= 5")
tf.flags.DEFINE_integer("random_state", None, "Random state.")
tf.flags.DEFINE_string("data_dir", "../data/dstc6-consumable/",
                       "Directory containing DSTC6 tasks")
tf.flags.DEFINE_string("logs_dir", "logs/",
                       "Directory to write logs")
tf.flags.DEFINE_string("model_dir", "model/",
                       "Directory containing memn2n model checkpoints")
tf.flags.DEFINE_string('loss_type', 'uniform', 'If weighted, use weighted loss function')
tf.flags.DEFINE_boolean('train', True, 'if True, begin to train')
tf.flags.DEFINE_boolean('interactive', False, 'if True, interactive')
tf.flags.DEFINE_boolean('OOV', False, 'if True, use OOV test set')
tf.flags.DEFINE_boolean('match_feature_flag', True, 'if True, include match feature')
tf.flags.DEFINE_float('loss_weight', 2.0, 'used when loss type is weighted, to bias the restaurant recommendation')

FLAGS = tf.flags.FLAGS

class chatBot(object):
    def __init__(self, data_dir, model_dir, logs_dir, task_id, isInteractive=True, OOV=False, memory_size=50, random_state=None, batch_size=32, learning_rate=0.01, epsilon=1e-8, max_grad_norm=40.0, evaluation_interval=10, hops=3, epochs=200, embedding_size=20, loss_type='uniform', loss_weight=2.0, match_feature_flag= False):
        self.data_dir = data_dir
        self.task_id = task_id
        self.model_dir = model_dir
        self.logs_dir = logs_dir
        # self.isTrain=isTrain
        self.isInteractive = isInteractive
        self.OOV = OOV
        self.memory_size = memory_size
        self.random_state = random_state
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epsilon = epsilon
        self.max_grad_norm = max_grad_norm
        self.evaluation_interval = evaluation_interval
        self.hops = hops
        self.epochs = epochs
        self.embedding_size = embedding_size
        self.loss_type = loss_type
        self.loss_weight = loss_weight
        self.match_feature_flag = match_feature_flag
        
        if OOV:
            print("Task ", task_id, " with OOV")
        else:
            print_str = ""
            print_str += ("Task " + str(task_id) + " (loss " + loss_type )
            if loss_type == "weighted":
                print_str += (", weight " + str(loss_weight))
            print(print_str + ")")
        print("")
        self.candidates, self.candid2indx = load_candidates(
            self.data_dir, self.task_id)
        self.n_cand = len(self.candidates)
        print("Candidate Size : ", self.n_cand)
        self.indx2candid = dict(
            (self.candid2indx[key], key) for key in self.candid2indx)

        # task data
        self.trainData, self.testData, self.valData = load_dialog_task(
            self.data_dir, self.task_id, self.candid2indx, self.OOV)
        data = self.trainData + self.testData + self.valData
        self.build_vocab(data, self.candidates)
        # self.candidates_vec = vectorize_candidates(
        #    candidates, self.word_idx, self.candidate_sentence_size)
        optimizer = tf.train.AdamOptimizer(
            learning_rate=self.learning_rate, epsilon=self.epsilon)
        self.sess = tf.Session()
        self.model = MemN2NDialog(self.batch_size, self.vocab_size, self.n_cand, self.sentence_size, self.embedding_size, session=self.sess,
                                  hops=self.hops, max_grad_norm=self.max_grad_norm, optimizer=optimizer, task_id=task_id, loss_type=loss_type, loss_weight=self.loss_weight)
        self.saver = tf.train.Saver(max_to_keep=50)

        #self.summary_writer = tf.summary.FileWriter(
        #    self.model.root_dir, self.model.graph_output.graph)

    def build_vocab(self, data, candidates):
        vocab = reduce(lambda x, y: x | y, (set(
            list(chain.from_iterable(s)) + q) for s, q, a, start in data))
        vocab |= reduce(lambda x, y: x | y, (set(candidate)
                                             for candidate in candidates))
        vocab |= {'MATCH_ATMOSPHERE_RESTRICTION'}
        vocab = sorted(vocab)
        self.word_idx = dict((c, i + 1) for i, c in enumerate(vocab))
        max_story_size = max(map(len, (s for s, _, _, _ in data)))
        mean_story_size = int(np.mean([len(s) for s, _, _, _ in data]))
        self.sentence_size = max(
            map(len, chain.from_iterable(s for s, _, _, _ in data)))
        self.candidate_sentence_size = max(map(len, candidates))
        query_size = max(map(len, (q for _, q, _, _ in data)))
        self.memory_size = min(self.memory_size, max_story_size)
        self.vocab_size = len(self.word_idx) + 1  # +1 for nil word
        self.sentence_size = max(
            query_size, self.sentence_size)  # for the position
        # params
        print("Vocab Size     : ", self.vocab_size)
        #print("Longest sentence length", self.sentence_size)
        #print("Longest candidate sentence length",self.candidate_sentence_size)
        #print("Longest story length", max_story_size)
        #print("Average story length", mean_story_size)

    def interactive(self):
        context = []
        u = None
        r = None
        nid = 1
        while True:
            line = raw_input('--> ').strip().lower()
            if line == 'exit':
                break
            if line == 'restart':
                context = []
                nid = 1
                print("clear memory")
                continue
            u = tokenize(line)
            data = [(context, u, -1)]
            s, q, a, c = vectorize_data(
                data, self.word_idx, self.sentence_size, self.batch_size, self.n_cand, self.memory_size, self.candidates, self.match_feature_flag)
            preds,_,_ = self.model.predict(s, q, c)
            r = self.indx2candid[preds[0]]
            print(r)
            r = tokenize(r)
            u.append('$u')
            u.append('#' + str(nid))
            r.append('$r')
            r.append('#' + str(nid))
            context.append(u)
            context.append(r)
            nid += 1

    def train(self):
        trainS, trainQ, trainA, trainC = vectorize_data(
            self.trainData, self.word_idx, self.sentence_size, self.batch_size, self.n_cand, self.memory_size, self.candidates, self.match_feature_flag)
        valS, valQ, valA, valC = vectorize_data(
            self.valData, self.word_idx, self.sentence_size, self.batch_size, self.n_cand, self.memory_size, self.candidates, self.match_feature_flag)
        n_train = len(trainS)
        n_val = len(valS)
        print("Training Size", n_train)
        print("Validation Size", n_val)
        tf.set_random_seed(self.random_state)
        batches = zip(range(0, n_train - self.batch_size, self.batch_size),
                      range(self.batch_size, n_train, self.batch_size))
        batches = [(start, end) for start, end in batches]
        best_validation_accuracy = 0

        for t in range(1, self.epochs + 1):
            np.random.shuffle(batches)
            total_cost = 0.0
            for start, end in batches:
                s = trainS[start:end]
                q = trainQ[start:end]
                a = trainA[start:end]
                c = trainC[start:end]
                a_type = self.classify_dialogs(a)
                cost_t = self.model.batch_fit(s, q, a, a_type, c)
                total_cost += cost_t
            if t % self.evaluation_interval == 0:
                train_preds,_,_,_ = self.batch_predict(trainS, trainQ, trainC, n_train)
                val_preds,_,_,_ = self.batch_predict(valS, valQ, valC, n_val)
                train_acc = metrics.accuracy_score(
                    np.array(train_preds), trainA)
                val_acc = metrics.accuracy_score(val_preds, valA)
                print('-----------------------')
                print('Epoch', t)
                print('Total Cost:', total_cost)
                print('Training Accuracy:', train_acc)
                print('Validation Accuracy:', val_acc)
                print('-----------------------')
                sys.stdout.flush()

                # write summary
                train_acc_summary = tf.summary.scalar(
                    'task_' + str(self.task_id) + '/' + 'train_acc', tf.constant((train_acc), dtype=tf.float32))
                val_acc_summary = tf.summary.scalar(
                    'task_' + str(self.task_id) + '/' + 'val_acc', tf.constant((val_acc), dtype=tf.float32))
                merged_summary = tf.summary.merge(
                    [train_acc_summary, val_acc_summary])
                summary_str = self.sess.run(merged_summary)
                #self.summary_writer.add_summary(summary_str, t)
                #self.summary_writer.flush()

                if val_acc > best_validation_accuracy:
                    best_validation_accuracy = val_acc
                    self.saver.save(self.sess, self.model_dir +
                                    'model.ckpt', global_step=t)

    def test(self):
        ckpt = tf.train.get_checkpoint_state(self.model_dir)
        if ckpt and ckpt.model_checkpoint_path:
            self.saver.restore(self.sess, ckpt.model_checkpoint_path)
        else:
            print("...no checkpoint found...")
        if self.isInteractive:
            self.interactive()
        else:
            testS, testQ, testA, testC, S_in_readable_form, Q_in_readable_form, last_db_results, dialogIDs  = vectorize_data_with_surface_form(
                self.testData, self.word_idx, self.sentence_size, self.batch_size, self.n_cand, self.memory_size, self.candidates, self.match_feature_flag)
            #testS, testQ, testA, testC = vectorize_data(
            #    self.testData, self.word_idx, self.sentence_size, self.batch_size, self.n_cand, self.memory_size, self.candidates)
            n_test = len(testS)
            test_preds,attn_weights,ranked_candidates_list,log_prob = self.batch_predict(testS, testQ, testC, n_test)
            test_acc = metrics.accuracy_score(test_preds, testA)
            match=0
            total=0
            all_data_points=[]
            for idx, val in enumerate(test_preds):
                #answer = self.indx2candid[testA[idx].item(0)]
                data_point={}
                context=[]
                for _, element in enumerate(S_in_readable_form[idx]):
                    context.append(element)
                data_point['context']=context
                data_point['query']=Q_in_readable_form[idx]
                #data_point['answer']=answer
                data_point['prediction']=self.indx2candid[val]
                data_point['dialog-id']=dialogIDs[idx]
                
                ranked_candidateids = ranked_candidates_list[idx]
                ranked_candidates = []
                for i in range(len(ranked_candidateids)):
                    ranked_candidates.append(self.indx2candid[ranked_candidateids[i]])
                data_point['ranked-candidates']=ranked_candidates
                all_data_points.append(data_point)
            
            file_prefix = self.logs_dir + 'task-'+str(self.task_id)+ '_hops-' + str(self.hops) + '_loss-' +str(self.loss_type)
            if self.loss_type == "weighted":
                file_prefix = file_prefix + '-'+str(self.loss_weight)   
            file_to_dump_json=  file_prefix + '.json'
            if self.OOV:
                file_to_dump_json= file_prefix + '-oov.json'
            
            with open(file_to_dump_json, 'w') as f:
                json.dump(all_data_points, f, indent=4)

            print("Test Size      : ", n_test)
            print("Test Accuracy  : ", test_acc)

            print("------------------------")

    def dstc_test_per_test_id(self, dstc_test_data, dstc_candidates, dstc_indx2candid, test_id):
        ckpt = tf.train.get_checkpoint_state(self.model_dir)
        if ckpt and ckpt.model_checkpoint_path:
            self.saver.restore(self.sess, ckpt.model_checkpoint_path)
        else:
            print("...no checkpoint found...")
        if self.isInteractive:
            self.interactive()
        else:
            #testS, testQ, testA, testC = vectorize_data(
            #   dstc_test_data, self.word_idx, self.sentence_size, self.batch_size, self.n_cand, self.memory_size, dstc_candidates, self.match_feature_flag)
            testS, testQ, testA, testC, S_in_readable_form, Q_in_readable_form, last_db_results, dialogIDs  = vectorize_data_with_surface_form(
                dstc_test_data, self.word_idx, self.sentence_size, self.batch_size, self.n_cand, self.memory_size, dstc_candidates, self.match_feature_flag)
            
            n_test = len(testS)
            test_preds,_,ranked_candidates_list, log_prob = self.batch_predict(testS, testQ, testC, n_test)
            all_data_points=[]
            for idx, val in enumerate(test_preds):
                data_point={}
                data_point['dialog-id']=dialogIDs[idx]

                ranked_candidateids = ranked_candidates_list[idx]
                log_prob_distr = log_prob[idx]
                ranked_candidates = []
                scores = []
                for i in range(len(ranked_candidateids)):
                    ranked_candidates.append(dstc_indx2candid[ranked_candidateids[i]])
                    scores.append(str(log_prob_distr[ranked_candidateids[i]]))
                data_point['ranked-candidates']=ranked_candidates
                data_point['scores']=scores
                all_data_points.append(data_point)
            
            file_prefix = self.logs_dir + 'task-'+str(self.task_id)+ '_tst-'+str(test_id)+ '_hops-' + str(self.hops) + '_loss-' +str(self.loss_type)
            if self.loss_type == "weighted":
                file_prefix = file_prefix + '-'+str(self.loss_weight)
            if self.match_feature_flag == True:
                file_prefix = file_prefix + 'with-mf' 
            file_to_dump_json=  file_prefix + '.json'
            
            with open(file_to_dump_json, 'w') as f:
                json.dump(all_data_points, f, indent=4)

            print("Test Size      : ", n_test)
            print("------------------------")

    def dstc_test(self):
        print("")
        for i in range(4):
            test_id = i+1
            print("Test ID : ", test_id)
            dstc_test_data = load_dialog_test_data(self.data_dir, self.task_id, test_id)
            dstc_candidates, dstc_candid2indx = load_test_candidates(self.data_dir, self.task_id, test_id)
            dstc_n_cand = len(dstc_candidates)
            print("Candidate Size : ", dstc_n_cand)
            dstc_indx2candid = dict((dstc_candid2indx[key], key) for key in dstc_candid2indx)
            self.dstc_test_per_test_id(dstc_test_data, dstc_candidates, dstc_indx2candid, test_id)
            sys.stdout.flush()

    def batch_predict(self, S, Q, C, n):
        preds = []
        attn_weights = []
        ranked_candidates_list = []
        log_prob_list = []
        for k in range(0,self.hops):
            attn_weights.append([])
        for start in range(0, n, self.batch_size):
            end = start + self.batch_size
            s = S[start:end]
            q = Q[start:end]
            c = C[start:end]
            pred, attn_arr, ranked_candidates, log_prob = self.model.predict(s, q, c)
            preds += list(pred)
            for k in range(0,self.hops):
                attn_weights[k].extend(attn_arr[k])
            ranked_candidates_list.extend(ranked_candidates)
            log_prob_list.extend(log_prob)
        return preds,attn_weights,ranked_candidates_list,log_prob_list

    def classify_dialogs(self, A):
        answer_type = []
        for idx in range(len(A)):
            answer = self.indx2candid[A[idx].item(0)]
            if "what do you think of this option:" in answer:
                answer_type.append(1)
            else:
                answer_type.append(0)
        return answer_type

    def close_session(self):
        self.sess.close()


if __name__ == '__main__':
    
    loss_weight_flag = ""
    if FLAGS.loss_type == "weighted":
        loss_weight_flag = "-" + str(FLAGS.loss_weight)

    match_feature_flag_str = ""
    if FLAGS.match_feature_flag:
        match_feature_flag_str = "_with-match-feature"
    model_dir = FLAGS.model_dir + "task" + str(FLAGS.task_id) + "_emb-" + str(FLAGS.embedding_size) + "_loss-" + str(FLAGS.loss_type) + loss_weight_flag + "_hops-" + str(FLAGS.hops) + match_feature_flag_str + "_model/"

    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    chatbot = chatBot(FLAGS.data_dir, model_dir, FLAGS.logs_dir, FLAGS.task_id, OOV=FLAGS.OOV,
                      isInteractive=FLAGS.interactive, batch_size=FLAGS.batch_size, epochs=FLAGS.epochs,
                      learning_rate = FLAGS.learning_rate, hops = FLAGS.hops, embedding_size = FLAGS.embedding_size,
                      loss_type = FLAGS.loss_type, loss_weight=FLAGS.loss_weight, match_feature_flag=FLAGS.match_feature_flag)
    # chatbot.run()
    
    if FLAGS.train:
        chatbot.train()
    else:
        chatbot.test()
    
    #chatbot.dstc_test()
    chatbot.close_session()
