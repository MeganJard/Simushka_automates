import pandas as pd
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from sklearn.metrics import classification_report
from torch.utils.data import DataLoader, Dataset



class DistilBERTClassifier:
    def __init__(self, model_path, tokenizer_name='distilbert-base-multilingual-cased', max_len=64):
        """
        Инициализация модели.

        :param model_path: Путь к сохраненной модели.
        :param tokenizer_name: Название токенизатора (по умолчанию DistilBERT).
        :param max_len: Максимальная длина последовательности.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = DistilBertTokenizer.from_pretrained(tokenizer_name)

        # Загрузка модели из локального файла
        self.model = DistilBertForSequenceClassification.from_pretrained(tokenizer_name, num_labels=2)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)

        self.max_len = max_len

    def predict(self, texts, batch_size=32):
        """
        Предсказание классов для списка текстов.

        :param texts: Список текстов.
        :param batch_size: Размер батча.
        :return: Предсказанные классы (0 или 1).
        """
        self.model.eval()
        predictions = []

        # Создаем Dataset и DataLoader
        dataset = self._create_dataset(texts)
        dataloader = DataLoader(dataset, batch_size=batch_size)

        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)

                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                _, preds = torch.max(outputs.logits, dim=1)
                predictions.extend(preds.cpu().numpy())

        return predictions

    def evaluate(self, texts, labels, batch_size=32):
        """
        Оценка модели на тестовых данных.

        :param texts: Список текстов.
        :param labels: Список истинных меток.
        :param batch_size: Размер батча.
        :return: Отчет о классификации.
        """
        predictions = self.predict(texts, batch_size)
        return classification_report(labels, predictions)

    def _create_dataset(self, texts):
        """
        Создание Dataset из списка текстов.

        :param texts: Список текстов.
        :return: Объект Dataset.
        """

        class TextDataset(Dataset):
            def __init__(self, texts, tokenizer, max_len):
                self.texts = texts
                self.tokenizer = tokenizer
                self.max_len = max_len

            def __len__(self):
                return len(self.texts)

            def __getitem__(self, idx):
                text = str(self.texts[idx])
                encoding = self.tokenizer.encode_plus(
                    text,
                    add_special_tokens=True,
                    max_length=self.max_len,
                    return_token_type_ids=False,
                    padding='max_length',
                    truncation=True,
                    return_attention_mask=True,
                    return_tensors='pt',
                )
                return {
                    'text': text,
                    'input_ids': encoding['input_ids'].flatten(),
                    'attention_mask': encoding['attention_mask'].flatten()
                }

        return TextDataset(texts, self.tokenizer, self.max_len)


# model_path = 'distilbert_model.pth'  # Путь к сохраненной модели
# classifier = DistilBERTClassifier(model_path)
# # Создание DataFrame
# df = pd.read_excel('ML_data.xlsx')[['Название товара на площадке', 'Название товара наше', 'Плохой артикул(1-да, пусто - нет)']]

# # Подготовка данных для модели
# texts = df['Название товара на площадке'] + " " + df['Название товара наше']
# labels = df['Плохой артикул(1-да, пусто - нет)']


# # Пример предсказания
# print("\nПример предсказания:")
# for i, row in df.iterrows():
#     try:
#         text = row['Название товара на площадке'] + " " + row['Название товара наше']
#         prediction = classifier.predict([text])[0]
#         print(f"Текст: {text} -> Предсказанный класс: {prediction} (Ожидаемый: {row['Плохой артикул(1-да, пусто - нет)']})")
#     except Exception as e:
#         pass
# print(classifier.predict('Barex Оксигент окислитель с эффектом блеска Joc Color	Barex Окислитель  JOC Color Shine Developer 3%(10vol), 150мл')[0])