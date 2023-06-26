import argparse

import httplib2
from googleapiclient.discovery import build
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('package_name',
                       help='The package name. Example: com.glow.android')
argparser.add_argument('-c', '--credentials', help='The credentials file. Example: /tmp/credentials.json',)
argparser.add_argument('-v', '--version_code', help='Version code to download', required=False)
argparser.add_argument('-f', '--aab', help='The aab path. Example: build/output/google/release/*.aab', required=False)


def get_service(credentials_file) -> ServiceAccountCredentials:
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_file, scopes='https://www.googleapis.com/auth/androidpublisher')

    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build('androidpublisher', 'v3', http=http)
    return service


def download_universal_apk(credentials_file, package_name, version_code='last'):
    service = get_service(credentials_file)

    try:
        edit_request = service.edits().insert(body={}, packageName=package_name)
        result = edit_request.execute()
        edit_id = result['id']

        bundle_result = service.edits().bundles().list(
            editId=edit_id, packageName=package_name).execute()
        bundles = bundle_result['bundles']
        print('existing versions: ')
        print('=====================')
        for bundle in bundles:
            print('versionCode: %s' % bundle['versionCode'])
        print('=====================')

        if version_code and version_code != 'last':
            bundles = [b for b in bundles if str(b['versionCode']) == version_code]
            if not bundles:
                print(f"bundle {version_code} does not exist")
                return
            else:
                bundle = bundles[0]
        elif bundles:
            bundle = bundles[-1]
        else:
            raise Exception('no existing bundles')

        version_code = bundle['versionCode']
        print('try download %s' % version_code)
        request = service.generatedapks().list(packageName=package_name, versionCode=version_code).execute()
        generated_apk = request['generatedApks'][0]
        universal_apk = generated_apk['generatedUniversalApk']
        download_request = service.generatedapks().download_media(packageName=package_name,
                                                                  versionCode=int(version_code),
                                                                  downloadId=universal_apk['downloadId']).execute()
        with open(f'{version_code}.apk', 'wb') as fw:
            fw.write(download_request)
            print('downloaded %s.apk' % version_code)

    except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run the '
              'application to re-authorize')


TRACK = 'internal'  # Can be 'alpha', beta', 'production' or 'rollout'


def upload_aab_and_download_universal_apk(credentials_file, package_name, aab_file):
    service = get_service(credentials_file)
    try:
        edit_request = service.edits().insert(body={}, packageName=package_name)
        result = edit_request.execute()
        edit_id = result['id']

        bundle_result = service.edits().bundles().list(
            editId=edit_id, packageName=package_name).execute()
        bundles = bundle_result['bundles']
        print('existing versions: ')
        print('=====================')
        for bundle in bundles:
            print('versionCode: %s' % bundle['versionCode'])
        print('=====================')

        upload_response = service.edits().bundles().upload(
            editId=edit_id,
            packageName=package_name,
            media_body=aab_file,
            media_mime_type="application/octet-stream").execute()
        print(upload_response)

        # track_response = service.edits().tracks().list(
        #     packageName=package_name,
        #     editId=edit_id,
        # ).execute()
        # print(track_response)

#         track_response = service.edits().tracks().update(
#             editId=edit_id,
#             track=TRACK,
#             packageName=package_name,
#             body={u'releases': [{
#                 u'name': str(upload_response['versionCode']),
#                 u'versionCodes': [str(upload_response['versionCode'])],
#                 # u'releaseNotes': [
#                 #     {u'text': u'Bundle recent changes in en-US'},
#                 # ],
#                 u'status': u'draft',
#             }]}).execute()
#         print(track_response)

        commit_request = service.edits().commit(
            editId=edit_id, packageName=package_name).execute()
        print(commit_request)

        download_universal_apk(credentials_file, package_name, str(upload_response['versionCode']))

    except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run the '
              'application to re-authorize')


def main():
    # Process flags and read their values.
    flags = argparser.parse_args()
    package_name = flags.package_name
    version_code = flags.version_code
    credentials_file = flags.credentials
    aab_file = flags.aab
    print(f'inputs: package_name:{package_name}, version_code(to download):{version_code}, aab_file:{aab_file}')
    if version_code:
        download_universal_apk(credentials_file, package_name, version_code)
    elif aab_file:
        try:
            upload_aab_and_download_universal_apk(credentials_file, package_name, aab_file)
        except:
            pass


if __name__ == '__main__':
    main()
