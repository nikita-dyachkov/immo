import json
import os
from typing import Optional, List

import strenum
from pydantic import BaseModel, Field, validator
from fastapi.encoders import jsonable_encoder
class ExtraField(strenum.StrEnum):
    BaseField = 'base_field'  # mapping
    AgencyField = 'agency_field'  # mapping
    Integer = 'integer_field'  # validate
    MaxLength = 'max_length_field'  # validate
    UnexpectedSymbols = 'unexpected_symbols_field'

class Listing(BaseModel):
    uid: str
    photos: List[str] = []
    # Base fields
    bathrooms: Optional[str] = Field(alias='bathrooms', extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    bedrooms: Optional[str] = Field(alias='bedrooms', extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    construction_year: Optional[str] = Field(alias='constructionYear',
                                             extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    description: Optional[str] = Field(alias='description', extra={ExtraField.BaseField: True,
                                                                   ExtraField.UnexpectedSymbols: True})
    energy_rating: Optional[str] = Field(alias='energyRating', extra={ExtraField.BaseField: True})
    features: Optional[str] = Field(alias='features', extra={ExtraField.BaseField: True})
    fire_type: Optional[str] = Field(alias='fireType', extra={ExtraField.BaseField: True})
    floor_type: Optional[str] = Field(alias='floorType', extra={ExtraField.BaseField: True, ExtraField.MaxLength: 32})
    garage: Optional[str] = Field(alias='garage', extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    heating: Optional[str] = Field(alias='heating', extra={ExtraField.BaseField: True, ExtraField.MaxLength: 64})
    latitude: Optional[float] = Field(alias='latitude', extra={ExtraField.BaseField: True})
    living_area: Optional[str] = Field(alias='livingArea', extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    location: Optional[str] = Field(alias='location', extra={ExtraField.BaseField: True})
    longitude: Optional[float] = Field(alias='longitude', extra={ExtraField.BaseField: True})
    parking: Optional[str] = Field(alias='parking', extra={ExtraField.BaseField: True, ExtraField.MaxLength: 32})
    plot_area: Optional[str] = Field(alias='plotArea', extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    price: Optional[str] = Field(alias='price', extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    price_from: Optional[str] = Field(alias='priceFrom', extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    ref: Optional[str] = Field(alias='ref', extra={ExtraField.BaseField: True, ExtraField.MaxLength: 64})
    rent_period: Optional[str] = Field(alias='rentPeriod', extra={ExtraField.BaseField: True})
    rent_price: Optional[str] = Field(alias='rentPrice', extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    rent_price_from: Optional[str] = Field(alias='rentPriceFrom',
                                           extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    rooms: Optional[str] = Field(alias='rooms', extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    subtype: Optional[str] = Field(alias='subtype', extra={ExtraField.BaseField: True, ExtraField.MaxLength: 64})
    title: Optional[str] = Field(alias='title', extra={ExtraField.BaseField: True, ExtraField.UnexpectedSymbols: True,
                                                       ExtraField.MaxLength: 128})
    terrace_area: Optional[str] = Field(alias='terraceArea', extra={ExtraField.BaseField: True})
    total_area: Optional[str] = Field(alias='totalArea', extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    transfer_price: Optional[str] = Field(alias='transferPrice',
                                          extra={ExtraField.BaseField: True, ExtraField.Integer: True})
    url: str = Field(alias='url', extra={ExtraField.BaseField: True, ExtraField.MaxLength: 1024})
    status: Optional[str] = Field(alias='status', extra={ExtraField.BaseField: True, ExtraField.MaxLength: 8})
    rent_status: Optional[str] = Field(alias='rentStatus', extra={ExtraField.BaseField: True, ExtraField.MaxLength: 8})

    # Agency fields
    company: Optional[str] = Field(alias='company', extra={ExtraField.AgencyField: True, ExtraField.MaxLength: 64})
    contacts: Optional[str] = Field(alias='contacts', extra={ExtraField.AgencyField: True, ExtraField.MaxLength: 64})
    listing_agent: Optional[str] = Field(alias='listing_agent',
                                         extra={ExtraField.AgencyField: True, ExtraField.MaxLength: 64})
    phone: Optional[str] = Field(alias='phone', extra={ExtraField.AgencyField: True, ExtraField.MaxLength: 32})
    is_private: Optional[bool] = Field(alias='is_private', extra={ExtraField.AgencyField: True})

    # Other fields
    currency: Optional[str]
    rent_currency: Optional[str]
    ref2: Optional[str]
    bank: Optional[str]
    root_location_ids: Optional[str] = Field(extra={ExtraField.MaxLength: 1024})

    class Config:
        """
        Provide config for listing model.
        """
        validate_assignment = True

    @validator('*')
    def validate_integer(cls, value, field):
        is_integer = field.field_info.extra.get('extra', {}).get(ExtraField.Integer)
        if is_integer and value and not value.isdigit():
            return None
        return value

    @validator('*')
    def validate_string_length(cls, value, field):
        max_length = field.field_info.extra.get('extra', {}).get(ExtraField.MaxLength)
        if max_length and value and len(value) > max_length:
            return value[:value.rfind(' ', 0, max_length)]
        return value

    @validator('*')
    def validate_unexpected_symbols(cls, value, field):
        is_unexpected_symbols = field.field_info.extra.get('extra', {}).get(ExtraField.UnexpectedSymbols)
        if is_unexpected_symbols and value:
            return ''.join([symbol for symbol in value if len(symbol.encode('utf-8')) < 3])
        return value



class Listings(BaseModel):
    listings: List[Listing] = []


def Immowelt_Json_To_Model(data):
    listings = Listings()
    for jsn in data.get('data'):
        if jsn.get('itemType') == 'PROJECT':
            prefix_for_url = 'https://www.immowelt.de/projekte/expose/'
        else:
            prefix_for_url = 'https://www.immowelt.de/expose/'
        uid = jsn.get('id')
        ref = jsn.get('onlineId')
        url = f'{prefix_for_url}{ref}'
        title = (jsn.get('title', ''))
        listing = Listing(uid=uid, url=url, ref=ref, title=title)
        listing.ref2 = jsn.get('projectId')
        listing.photos = [image.get('imageUri') for image in jsn.get('pictures')]
        listing.features = ', '.join([feature for feature in jsn.get('features')])
        listing.construction_year = jsn.get('constructionYear')
        listing.subtype = jsn.get('estateTypes')[0]
        coord = jsn.get('place').get('point', {})
        listing.latitude = coord.get('lat')
        listing.longitude = coord.get('lon')
        listing.rooms = jsn.get('roomsMin')
        listing.company = jsn.get('broker').get('companyName')
        listing.root_location_ids=313123
        place = jsn.get('place')
        city = place.get('city')
        district = place.get('district')
        postcode = place.get('postcode')
        street = place.get('street')
        houseNumber = place.get('houseNumber')
        listing.location = ', '.join(map(str, filter(None, [city, district, postcode, street, houseNumber])))
        for area in jsn.get('areas'):
            if area.get('type') == 'LIVING_AREA':
                listing.living_area = area.get('sizeMin')
            elif area.get('type') == 'PLOT_AREA':
                listing.plot_area = area.get('sizeMin')
        primary_price = jsn.get('primaryPrice')
        if 'RENT' in primary_price.get('type'):
            listing.rent_price = primary_price.get('amountMin')
        elif 'PURCHASE' in primary_price.get('type'):
            listing.price = primary_price.get('amountMin')
        if 'SALE' in jsn.get('distributionType'):
            listing.status = 'active'
        elif 'RENT' in jsn.get('distributionType'):
            listing.rent_status = 'active'
        listings.listings.append(listing)
    return listings


def Immobilienscout24_Json_To_Model(data):
    listings = Listings()
    prefix_for_url = 'https://www.immobilienscout24.de/expose/'
    for jsn in data.get('searchResponseModel').get('resultlist.resultlist').get('resultlistEntries')[0].get(
            'resultlistEntry'):
        estate = jsn.get('resultlist.realEstate', {})
        uid = jsn.get('@id')
        ref = jsn.get('realEstateId')
        url = f'{prefix_for_url}{ref}'
        title = (estate.get('title', ''))
        listing = Listing(uid=uid, ref=ref, url=url, title=title, )
        features = jsn.get('realEstateTags', {})
        if features:
            features=features.get('tag','')
        if type(features) is list:
            features = ', '.join(features)
        listing.features = features
        listing.living_area = estate.get('livingSpace')
        listing.rooms = estate.get('numberOfRooms')
        listing.root_location_ids = 412312
        listing.energy_rating = estate.get('energyEfficiencyClass')
        listing.company = estate.get('realtorCompanyName')
        listing.subtype = estate.get('@xsi.type')
        photos = []
        attachments = estate.get('galleryAttachments', {}).get('attachment')
        if type(attachments) is list:
            for attachment in attachments:
                try:
                    for image in attachment.get('urls', []):
                        photos.append(image.get('url', {}).get('@href'))
                except AttributeError as e:
                    print(uid)
                    print(e)
        else:
            try:
                for image in attachments.get('urls', []):
                    photos.append(image.get('url', {}).get('@href'))
            except AttributeError as e:
                print(uid)
                print(e)
        listing.photos = photos
        address = estate.get('address')
        city = address.get('city')
        quarter = address.get('quarter')
        postcode = address.get('postcode')
        street = address.get('street')
        houseNumber = address.get('houseNumber')
        listing.location = ', '.join(map(str, filter(None, [city, quarter, postcode, street, houseNumber])))
        coord = address.get('wgs84Coordinate', {})
        listing.latitude = coord.get('latitude')
        listing.longitude = coord.get('longitude')
        contacts = estate.get('contactDetails')
        first_name = contacts.get('firstname')
        last_name = contacts.get('lastname')
        listing.phone = contacts.get('phoneNumber')
        listing.listing_agent = f'{first_name} {last_name}'
        price = estate.get('price')
        if 'PURCHASE' in price.get('marketingType'):
            listing.status = 'active'
            listing.price = price.get('value')
        elif 'RENT' in price.get('marketingType'):
            listing.rent_status = 'active'
            listing.rent_price = price.get('value')
            listing.rent_period = price.get('priceIntervalType')
        listings.listings.append(listing)
    return listings


if __name__ == '__main__':
    dir_path = f'data/'

    if not os.path.exists(f'{dir_path}'):
        os.makedirs(f'{dir_path}')


    with open('immowelt.json', 'r') as f:
        data = json.load(f)
        file_name='immowelt_parsed.json'
        with open(f'{dir_path}/{file_name}', 'a') as file_handle:
            file_handle.write(str(jsonable_encoder(Immowelt_Json_To_Model(data=data).listings)))
    with open('immoscout.json', 'r') as f:
        data = json.load(f)
        file_name = 'immoscout_parsed.json'
        with open(f'{dir_path}/{file_name}', 'a') as file_handle:
            file_handle.write(str(jsonable_encoder(Immobilienscout24_Json_To_Model(data=data).listings)))
