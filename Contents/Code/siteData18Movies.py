import PAsearchSites
import PAutils
import siteData18Scenes

def search(results, lang, siteNum, searchData):
    searchResults = []
    siteResults = []
    temp = []
    count = 0

    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]

        if int(sceneID) > 100:
            searchData.title = searchData.title.replace(sceneID, '', 1).strip()
            movieURL = '%s/movies/%s' % (PAsearchSites.getSearchBaseURL(siteNum), sceneID)
            searchResults.append(movieURL)

    searchData.encoded = searchData.title.replace(',', '').replace('& ', '')
    searchURL = '%s%s' % (PAsearchSites.getSearchSearchURL(siteNum), searchData.encoded)
    req = PAutils.HTTPRequest(searchURL, headers={'Referer': 'https://www.data18.com'})
    searchPageElements = HTML.ElementFromString(req.text)

    for searchResult in searchPageElements.xpath('//a'):
        movieURL = searchResult.xpath('./@href')[0].split('-')[0]

        if ('/movies/' in movieURL and movieURL not in searchResults):
            urlID = re.sub(r'.*/', '', movieURL).split('-')[0]

            titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//p[@class="gen12 bold"]')[0].text_content(), siteNum)
            curID = PAutils.Encode(movieURL)
            siteResults.append(movieURL)

            try:
                date = searchResult.xpath('.//span[@class="gen11"]/text()')[0].strip()
            except:
                date = ''

            if date and not date == 'unknown':
                releaseDate = datetime.strptime(date, "%B, %Y").strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''
            displayDate = releaseDate if date else ''

            if sceneID == urlID:
                score = 100
            elif searchData.date and displayDate:
                score = 80 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            if score > 70:
                sceneURL = PAutils.Decode(curID)
                req = PAutils.HTTPRequest(sceneURL)
                detailsPageElements = HTML.ElementFromString(req.text)

                # Studio
                try:
                    studio = detailsPageElements.xpath('//b[contains(., "Network")]//following-sibling::b')[0].text_content().strip()
                except:
                    try:
                        studio = detailsPageElements.xpath('//b[contains(., "Studio")]//following-sibling::b')[0].text_content().strip()
                    except:
                        try:
                            studio = detailsPageElements.xpath('//p[contains(., "Site:")]//following-sibling::a[@class="bold"]')[0].text_content().strip()
                        except:
                            studio = ''

                if score == 80:
                    count += 1
                    temp.append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))
                else:
                    results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))

                #Split Scenes
                sceneCount = detailsPageElements.xpath('//text()[contains(., "Scenes:")]')[0].split(':')[-1].strip()
                if sceneCount.isdigit():
                    sceneCount = int(sceneCount)
                else:
                    sceneCount = 0

                for sceneNum in range(1, sceneCount + 1):
                    section = "Scene " + str(sceneNum)
                    scene = PAutils.Encode(detailsPageElements.xpath('//a[contains(., "%s")]/@href' % (section))[0])

                    if score == 80:
                        count += 1
                        temp.append(MetadataSearchResult(id='%s|%d|%s|%s|%d' % (scene, siteNum, releaseDate, titleNoFormatting, sceneNum), name='%s [%s][%s] %s' % (titleNoFormatting, section, studio, displayDate), score=score, lang=lang))
                    else:
                        results.Append(MetadataSearchResult(id='%s|%d|%s|%s|%d' % (scene, siteNum, releaseDate, titleNoFormatting, sceneNum), name='%s [%s][%s] %s' % (titleNoFormatting, section, studio, displayDate), score=score, lang=lang))
            else:
                if score == 80:
                    count += 1
                    temp.append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s %s' % (titleNoFormatting, displayDate), score=score, lang=lang))
                else:
                    results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s %s' % (titleNoFormatting, displayDate), score=score, lang=lang))

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for movieURL in googleResults:
        movieURL = movieURL.replace('http:', 'https:')
        if ('/movies/' in movieURL and '.html' not in movieURL and movieURL not in searchResults and movieURL not in siteResults):
            searchResults.append(movieURL)

    for movieURL in searchResults:
        req = PAutils.HTTPRequest(movieURL)
        detailsPageElements = HTML.ElementFromString(req.text)
        urlID = re.sub(r'.*/', '', movieURL)

        # Studio
        try:
            studio = detailsPageElements.xpath('//b[contains(., "Network")]//following-sibling::b')[0].text_content().strip()
        except:
            try:
                studio = detailsPageElements.xpath('//b[contains(., "Studio")]//following-sibling::b')[0].text_content().strip()
            except:
                try:
                    studio = detailsPageElements.xpath('//p[contains(., "Site:")]//following-sibling::a[@class="bold"]')[0].text_content().strip()
                except:
                    studio = ''

        titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content(), siteNum)
        curID = PAutils.Encode(movieURL)

        try:
            date = detailsPageElements.xpath('//@datetime')[0].strip()
        except:
            date = ''

        if date and not date == 'unknown':
            releaseDate = parse(date).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''
        displayDate = releaseDate if date else ''

        if sceneID == urlID:
            score = 100
        elif searchData.date and displayDate:
            score = 80 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        if score == 80:
            count += 1
            temp.append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))
        else:
            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))

        #Split Scenes
        sceneCount = detailsPageElements.xpath('//text()[contains(., "Scenes:")]')[0].split(':')[-1].strip()

        if sceneCount.isdigit():
            sceneCount = int(sceneCount)
        else:
            sceneCount = 0

        for sceneNum in range(1,sceneCount + 1):
            section = "Scene " + str(sceneNum)
            scene = PAutils.Encode(detailsPageElements.xpath('//a[contains(., "%s")]/@href' % (section))[0])

            if score == 80:
                count += 1
                temp.append(MetadataSearchResult(id='%s|%d|%s|%s|%d' % (scene, siteNum, releaseDate, titleNoFormatting, sceneNum), name='%s [%s][%s] %s' % (titleNoFormatting, section, studio, displayDate), score=score, lang=lang))
            else:
                results.Append(MetadataSearchResult(id='%s|%d|%s|%s|%d' % (scene, siteNum, releaseDate, titleNoFormatting, sceneNum), name='%s [%s][%s] %s' % (titleNoFormatting, section, studio, displayDate), score=score, lang=lang))

    for result in temp:
        if count > 1 and result.score == 80:
            results.Append(MetadataSearchResult(id=result.id, name=result.name, score=79, lang=lang))
        else:
            results.Append(MetadataSearchResult(id=result.id, name=result.name, score=result.score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    if len(metadata_id) > 3:
        Log('Switching to Data18Scenes')
        siteData18Scenes.update(metadata, lang, siteNum, movieGenres, movieActors)
        return metadata

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content(), siteNum)

    # Summary
    summary = detailsPageElements.xpath('//div[@class="gen12"]//div[contains(., "Description")]')[1].text_content().split('---')[-1].split('Description -')[-1].strip()
    if len(summary) > 1:
        metadata.summary = summary

    # Studio
    try:
        studio = detailsPageElements.xpath('//b[contains(., "Network")]//following-sibling::b')[0].text_content().strip()
    except:
        try:
            studio = detailsPageElements.xpath('//b[contains(., "Studio")]//following-sibling::b')[0].text_content().strip()
        except:
            try:
                studio = detailsPageElements.xpath('//p[contains(., "Site:")]//following-sibling::a[@class="bold"]')[0].text_content().strip()
            except:
                studio = ''

    if studio:
        metadata.studio = studio

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.collections.add(metadata.studio)
    try:
        tagline = detailsPageElements.xpath('//p[contains(., "Movie Series")]//a[@title]')[0].text_content().strip()
        metadata.collections.add(tagline)
    except:
        pass

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    else:
        date_object = parse(detailsPageElements.xpath('//@datetime')[0].strip())
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//p[./b[contains(., "Categories")]]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//b[contains(., "Cast")]//following::div//a[contains(@href, "/pornstars/")]//img')
    for actorLink in actors:
        actorName = actorLink.xpath('./@alt')[0].strip()
        actorPhotoURL = actorLink.xpath('./@data-original')[0].strip()

        if actorName:
            movieActors.addActor(actorName, actorPhotoURL)

    # Director
    metadata.directors.clear()
    director = metadata.directors.new()
    try:
        directorName = detailsPageElements.xpath('//p[./b[contains(., "Director")]]')[0].text_content().split(':')[2].strip()
        if not directorName == 'Unknown':
            director.name = directorName
    except:
        pass

    # Posters
    art = []
    xpaths = [
        '//a[@id="enlargecover"]//@href',
        '//img[@id="backcoverzone"]//@src',
        '//img[@id="imgposter"]//@src',
        '//img[contains(@src, "th8")]/@src',
        '//img[contains(@data-original, "th8")]/@data-original',
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            art.append(img)

    try:
        galleries = detailsPageElements.xpath('//div[@id="galleriesoff"]//div')
        movieID = re.sub(r'.*/', '', sceneURL)

        for gallery in galleries:
            galleryID = gallery.xpath('./@id')[0].replace('gallery', '')
            photoViewerURL = ("%s/sys/media_photos.php?movie=%s&pic=%s" % (PAsearchSites.getSearchBaseURL(siteNum), movieID[1:], galleryID))
            req = PAutils.HTTPRequest(photoViewerURL)
            photoPageElements = HTML.ElementFromString(req.text)

            for xpath in xpaths:
                for img in photoPageElements.xpath(xpath):
                    art.append(img.replace('/th8', '').replace('-th8', ''))
    except:
        pass

    images = []
    posterExists = False
    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://www.data18.com'})
                images.append(image)
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if height > width:
                    # Item is a poster
                    posterExists = True
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    if not posterExists:
        for idx, image in enumerate(images, 1):
            try:
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[art[idx - 1]] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
