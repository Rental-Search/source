# -*- coding: utf-8 -*-
import os
from decimal import Decimal as D
import datetime

from django.core.files import File
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TransactionTestCase

from products.models import (Picture, Product, ProductReview, PatronReview, 
    CarProduct, RealEstateProduct)

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)


class ProductTest(TransactionTestCase):
    fixtures = ['category', 'patron', 'address', 'price', 'product']
    reset_sequences = True
    
    @transaction.commit_on_success
    def test_product_creation(self):
        product = Product(
            summary="Perceuse visseuse Philips",
            deposit_amount=250,
            description=u"Engrenage planétaire à haute performance 2 vitesses : durée de vie supérieure, transmission optimale, fonctionnement régulier.",
            address_id=1,
            quantity=1,
            category_id=35,
            owner_id=1
        )
        product.save()

    @transaction.commit_on_success
    def test_carproduct_creation(self):
        carproduct = CarProduct(
            summary="Opel Corsa",
            brand="Opel",
            model="Corsa",
            deposit_amount=250,
            description=u"Opel Corsa en bonne etat. Asd asd.",
            address_id=1,
            quantity=1,
            category_id=35,
            owner_id=1,
            air_conditioning=False,
            power_steering=False,
            cruise_control=False,
            gps=False,
            baby_seat=False,
            roof_box=False,
            bike_rack=False,
            snow_tires=False,
            snow_chains=False,
            ski_rack=False,
            cd_player=False,
            audio_input=False,
            tax_horsepower=D('1.00'),
            licence_plate='05 asd 50',
            first_registration_date=datetime.date(2010, 9, 5)
        )
        carproduct.save()
        self.assertEqual(CarProduct.objects.count(), 1)
        self.assertTrue(carproduct.product_ptr)

    @transaction.commit_on_success
    def test_realestateproduct_creation(self):
        realestateproduct = RealEstateProduct(
            summary="appart a paris",
            deposit_amount=250,
            description=u"Paris, paris.",
            address_id=1,
            quantity=1,
            category_id=35,
            owner_id=1,
            air_conditioning=False,
            breakfast=False,
            balcony=False,
            lockable_chamber=False,
            towel=False,
            lift=False,
            family_friendly=False,
            gym=False,
            accessible=False,
            heating=False,
            jacuzzi=False,
            chimney=False,
            internet_access=False,
            kitchen=False,
            parking=False,
            smoking_accepted=False,
            ideal_for_events=False,
            tv=False,
            washing_machine=False,
            tumble_dryer=False,
            computer_with_internet=False,
        )
        realestateproduct.save()
        self.assertEqual(RealEstateProduct.objects.count(), 1)
        self.assertTrue(realestateproduct.product_ptr)

class PictureTest(TransactionTestCase):
    reset_sequences = True

    def test_ensure_delete(self):
        f = open(local_path('../fixtures/bentley.jpg'))
        picture = Picture.objects.create(image=File(f))
        image_path = picture.image.path
        self.assertTrue(os.path.exists(image_path))
        picture.delete()
        self.assertFalse(os.path.exists(image_path))
    

class ProductReviewTest(TransactionTestCase):
    reset_sequences = True
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'booking']
    
    def test_score_values_negative(self):
        review = ProductReview(score=-1.0, product_id=1, description='Incorrect', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_too_high(self):
        review = ProductReview(score=2.0, product_id=1, description='Parfait', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_correct(self):
        try:
            review = ProductReview(score=0.5, product_id=1, description='Correct', reviewer_id=2)
            review.full_clean()
        except ValidationError, e:
            self.fail(e)
    
    def test_owner_review(self):
        review = ProductReview(score=2.0, product_id=1, description='Parfait', reviewer_id=1)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_booking_review(self):
        review = ProductReview(score=2.0, product_id=2, description='Parfait', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    

class PatronReviewTest(TransactionTestCase):
    reset_sequences = True
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'booking']
    
    def test_score_values_negative(self):
        review = PatronReview(score=-1.0, patron_id=1, description='Incorrect', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_too_high(self):
        review = PatronReview(score=2.0, patron_id=1, description='Parfait', reviewer_id=2)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_score_values_correct(self):
        try:
            review = PatronReview(score=0.5, patron_id=1, description='Correct', reviewer_id=2)
            review.full_clean()
        except ValidationError, e:
            self.fail(e)
    
    def test_patron_review(self):
        review = PatronReview(score=2.0, patron_id=1, description='Correct', reviewer_id=1)
        self.assertRaises(ValidationError, review.full_clean)
    
    def test_booking_review(self):
        review = PatronReview(score=2.0, patron_id=2, description='Correct', reviewer_id=1)
        self.assertRaises(ValidationError, review.full_clean)
    
