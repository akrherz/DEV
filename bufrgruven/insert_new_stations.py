"""Convert a station list into what BUFRGRUVEN expects."""

from pyiem.database import with_sqlalchemy_conn

NEWLIST = """000530	 LIW	Near Long Isl Twin Frk	 NY
000531	 CEA	Charleston Exec Airport  SC
000532	 WINM	Windigo 		 MI
000533	 HERM	Herman			 MI
000534	 KUAO	Aurora Airport		 OR
000535	 PHHN	Hana Airport		 HI
000536	 HLKL	Haleakala Summit	 HI
000537	 MKEA	Mauna Kea Summit	 HI
000538	 PHBK	Barking Sands		 HI
000539	 PHUP	Upolu Airport		 HI
000540	 MLOA	Mauna Loa Summit	 HI
000541	 PMDY	Henderson Field 	 HI
000542	 HI01	Princeville Airport	 HI
000543	 PHNG	Kaneohe Bay MCAS	 HI
000544	 SCPE	South Cape		 HI
000545	 GBO	Green Bank Observatory	 WV
000546	 MALO	Malone			 NY
000547	 CLCR	Colchester Reef 	 VT
000548	 ALBU	Albaugh 		 VT
000549	 KLGN	Killington Peak 	 VT
000550	 NUND	North Underhill 	 VT
000551	 RIPT	Ripton			 VT
000552	 KJFX	Jasper			 AL
000553	 KALX	Alexander City		 AL
000554	 KJZI	Charleston Exec Airport  SC
000555	 KDSV	Dansville		 NY
000556	 NCPE	North Cape		 FL
000557	 JAXX	Off Jacksonville	 FL
000558	 PENX	Off Pensacola		 FL
000559	 TPXX	Off Tampa		 FL
000560	 TLHX	Off Tallahassee 	 FL
000561	 DABX	Off Daytona Beach	 FL
000562	 PANX	Off Panama City 	 FL
000563	 KS12	Albany			 OR
000564	 PRKD	Parkdale		 OR
000565	 OC29	Buoy 29 		 OR
000566	 OC50	Buoy 50 		 OR
000567	 OC89	Buoy 89 		 OR
000568	 KRGA	Central KY Region Arpt	 KY
000569	 AEJ	Buena Vista Airport	 CO
000570	 ESTP	Estes Park		 CO
000571	 CANO	Canon City		 CO
000572	 GSH	Goshen Municipal Arpt	 IN
000573	 ANQ	Angola Airport		 IN
000574	 SYSE	Syracuse		 KS
000575	 OWD	Norwood Memorial Arpt	 MA
000576	 FIT	Fitchburg (ASOS)	 MA
000577	 GRNF	Greenfield		 MA
000578	 GLOU	Gloucester		 MA
000579	 TAN	Taunton (ASOS)		 MA
000580	 NTHH	Northampton		 MA
000581	 FDK	Frederick Muni Airport	 MD
000582	 GAI	Gaithersburg		 MD
000583	 IZG	Fryeburg (ASOS) 	 ME
000584	 NERA	New Era 		 MI
000585	 ARB	Ann Arbor Muni (ASOS)	 MI
000586	 GPZ	Grand Rapids (AWOS)	 MN
000587	 ROS	Rush City		 MN
000588	 8Y2	Buffalo Muni Airport	 MN
000589	 ANE	Minneapolis/Blaine	 MN
000590	 CKC	Grand Marais/Cook Co	 MN
000591	 KRPX	Roundup 		 MT
000592	 KCMA	Kancamagus Pass 	 NH
000593	 SKX	TAOS Muni Airport (AWOS) NM
000594	 LAM	Los Alamos Airport	 NM
000595	 29G	Ravenna Portage Co Arpt  NM
000596	 VES	Versailles Dark Co Arpt  OH
000597	 THV	York Airport (ASOS)	 PA
000598	 PTTO	Pottstown		 PA
000599	 WDFD	Woodford State Park	 VT
000600	 ASWI	Ashland Airport 	 WI
000605	 SHD	Staunton/Shenandoah	 VA
000615	 KHAF	Half Moon Bay Airport	 CA
000616	 KSVR	South Valley Airport	 UT
001007	 KSEZ	Sedona Airport		 AZ 34.85 -111.78
001008	 KPAN	Payson Airport		 AZ 34.26 -111.34
001009	 KJTC	Springerville Muni Arpt  AZ 34.13 -109.31
001010	 KCMR	Williams		 AZ 35.31 -112.19
001011	 KRQE	Window Rock (ASOS)	 AZ 35.65 -109.07
001012	 TUBA	Tuba City		 AZ 36.14 -111.24
001013	  CHN	Chinle			 AZ 36.15 -109.55
001014	  JLK	Jacob Lake		 AZ 36.71 -112.22
001015	 KAYA	Kayenta 		 AZ 36.73 -110.25
001016	  SUP	Supai			 AZ 36.24 -112.69
001017	 PCHS	Peach Springs		 AZ 35.53 -113.43
001018	  BDD	Bagdad			 AZ 34.58 -113.18
001019	  SMA	Second Mesa		 AZ 35.79 -110.51
001020	  TNP	TEEC NOS POS		 AZ 36.92 -109.09
001021	  BOP	Buffalo Pass		 AZ 36.47 -109.15
001500	 LGAV	Athens, Greece
001501	 MBPV	Providenciales, Turks and Caicos
001502	 UHMM	Magadan, Russia
001503	 UHPP	Petropavlovsk, Russia
001504	 USNN	Nizhnevartovsk, Russia
039690	 EIDW	Dublin, Ireland
066700	 LSZH	Zurich, Switzerland
068368	 FAJS	Johannesburg / Tambo, South Africa
071570	 LFPG	Paris/Roissy-en-France
076900	 LFMN	Nice, France
082210	 LEMD	Madrid, Spain
085150	 LPAZ	Santa Maria Island, Portugal
085360	 LPPT	Lisbon, Portugal
160660	 LIMC	Milano/Milan, Italy
233300	 USDD	Salekhard, Russia
303090	 UIBB	Bratsk, Russia
307100	 UIII	Dzerzhinsk, Russia
317350	 UHHH	Khabarovsk, Russia
401800	 LLBG	Tel Aviv, Israel
471130	 RKSI	Seoul Incheon, South Korea
471280	 RKTU	Chongiu, South Korea
471820	 RKPC	Cheju, South Korea
478080	 RJFF	Fukuoka, Japan
489910	 VDPP	Phnom-Penh, Cambodia
618320	 GUCY	Conarky, Guinea
619800	 FMEE	Roland Garros, Reunion
722267	 KTOI	Troy Municipal Airport	AL
724458	 KJEF	Jefferson City Airport	MO
726963	 KTMK	Tillamook		OR
789480	 TLPL	Hewandorra, St. Lucia
789580	 TGPY	St. Georges, Grenada
845150	 SPCL	Pucallpa, Peru"""


@with_sqlalchemy_conn("mesosite")
def main(conn=None):
    """Go Main Go."""
    # Manual provided via email thread with Jason Levit
    stations = {}
    with open("/home/akrherz/Downloads/bufr_stalist.meteo.gfs") as fh:
        for line in fh:
            lat = line[7:14].strip()
            if lat.endswith("S"):
                lat = -1 * float(lat[:-1])
            else:
                lat = float(lat[:-1])
            lon = line[14:21].strip()
            if lon.endswith("W"):
                lon = -1 * float(lon[:-1])
            else:
                lon = float(lon[:-1])
            stations[line[:6]] = {
                "icao": line[22:26].strip(),
                "name": line[30:53].strip(),
                "source": line[62:].strip(),
                "lat": lat,
                "lon": lon,
                "code": line[27:29],
                "elev": line[57:61],
                "state": line[53:55],
            }

    for line in NEWLIST.split("\n"):
        tokens = line.split()
        idnum = tokens[0]
        meta = stations[idnum]
        print(
            f"{idnum} {meta['lat']:8.3f} {meta['lon']:9.3f} "
            f" {meta['icao']:4s}  {meta['code']}  0 {meta['name']:32.32s} "
            f"{meta['state']:2s} {meta['elev']:>8s}   {meta['source']}"
        )


if __name__ == "__main__":
    main()
