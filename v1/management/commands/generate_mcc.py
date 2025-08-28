from django.core.management.base import BaseCommand

from v1.models import MCC


class Command(BaseCommand):
    help = 'Generatsiya qiladi eng ko‘p ishlatiladigan MCC kodlarini'

    def handle(self, *args, **kwargs):
        self.generate_mcc()

    def generate_mcc(self):
        """Eng ko‘p ishlatiladigan MCC kodlarini bazaga qo‘shadi"""
        mcc_list = [
            (5411, "Oziq-ovqat do‘konlari, supermarketlar"),
            (5812, "Restoranlar, fast food"),
            (5814, "Tez tayyorlanadigan ovqat (fast food)"),
            (5912, "Dorixonalar"),
            (5813, "Bar va kafelar"),
            (5541, "Yoqilg‘i quyish shoxobchalari (gas stations)"),
            (4111, "Mahalliy va shaharlararo avtobuslar"),
            (4789, "Transport xizmatlari (taksi, yuk tashish)"),
            (5941, "Sport va o‘yin jihozlari do‘konlari"),
            (5691, "Tikuvchilik va kiyim do‘konlari"),
            (5732, "Kompyuter va dasturiy ta’minot do‘konlari"),
            (5811, "Restoranlar (umumiy)"),
            (5921, "Alkoholli ichimliklar do‘konlari"),
            (5922, "Chekish mahsulotlari do‘konlari"),
            (5960, "Onlayn xizmatlar, elektron tijorat"),
            (5999, "Turli chakana savdo (boshqa)"),
            (4784, "Sayohat va turistik xizmatlar"),
            (6011, "Bankomatlar (ATM)"),
            (6012, "Bank kartalari orqali to‘lov xizmatlari"),
        ]

        for code, desc in mcc_list:
            obj, created = MCC.objects.get_or_create(
                code=code,
                defaults={'description': desc}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'MCC {code} added.'))
            else:
                self.stdout.write(f'MCC {code} already exists.')
