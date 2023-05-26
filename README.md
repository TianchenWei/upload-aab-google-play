# GitHub Action: Upload AAB to Google Play Console and Download APK

This GitHub Action workflow is designed to upload an Android App Bundle (AAB) file to the Google Play Console and download the corresponding universal APK (Android Package) for the latest release. It utilizes the Google Play Developer Publishing API for this purpose.

## Inputs

The workflow accepts the following inputs:

- **service-account-credential-base64**: Base64-encoded service account credentials required to access the Google Play Console. This input is mandatory.

- **package-name**: The package name of your Android app. This input is mandatory.

- **aab-file-path**: The file path to the AAB file that needs to be uploaded. This input is mandatory.

## Outputs

The workflow provides the following output:

- **universal-apk-file-path**: The file path of the downloaded universal APK for the latest release.

## Usage

To use this GitHub Action in your workflow, follow these steps:

1. Configure a Google service account by following the instructions in the [Google documentation](https://developers.google.com/android-publisher/getting_started#configure).

2. Base64 encode the downloaded service account credential file.

3. Save the base64-encoded service account credentials as a secret in your GitHub repository. Refer to the [GitHub Actions documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository) for detailed instructions on managing secrets.

4. Add the following step to your workflow file, replacing the input values with your own:

```yaml
      - id: upload-google
        name: Upload Google Play Console
        uses: TianchenWei/upload-aab-google-play@main
        with:
          package-name: your-app-application-id
          aab-file-path: your-aab-file-path
          service-account-credential-base64: ${{ secrets.your-service-account-credential-base64 }}
```

Make sure to replace `your-app-application-id` with the actual package name of your Android app, `your-aab-file-path` with the path to your AAB file, and `your-service-account-credential-base64` with the name of the secret storing the base64-encoded service account credentials.

After completing these steps, the workflow will execute the `upload-aab-google-play` action, uploading the AAB file to the Google Play Console and downloading the universal APK file for the latest release. The file path of the downloaded APK will be available as the `universal-apk-file-path` output.
